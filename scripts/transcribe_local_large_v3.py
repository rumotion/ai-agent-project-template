#!/usr/bin/env python3
"""Transcribe audio or video LOCALLY with whisper large-v3. Nothing leaves the machine.

Standing rule: always large-v3, never a smaller model. Proper-noun accuracy
is what this workstation runs on.

Execution strategy:
  1. GPU-First (faster-whisper / CTranslate2 on NVIDIA GPU):
     - Tier 1: CUDA float16 (highest quality and throughput, ~4-5 GB VRAM)
     - Tier 2 (OOM fallback): CUDA int8_float16 (~2.5-3.2 GB VRAM)
  2. CPU Fallback (if CUDA is unavailable or GPU OOMs):
     - Parallel workers on silence-detected chunks, merging timestamps.

Language is detected once on the first 30 s with `tiny` and forced on `large-v3`,
so no segment mis-detects.

Usage:
    python -m skills.local-media-transcription.scripts.transcribe <media-file> [output-dir]
    or
    python transcribe.py <media-file> [output-dir]

Outputs <stem>_large-v3.txt (timestamped lines) and <stem>_large-v3.srt.
"""

from __future__ import annotations

import concurrent.futures as cf
import ctypes
import os
import re
import subprocess
import sys
import time

MODEL = "large-v3"
MIN_CHUNK = 90.0     # never cut finer than this for CPU chunking
MAX_CHUNK = 300.0    # never let a chunk exceed this for CPU chunking
RAM_PER_WORKER_GB = 9  # large-v3 fp32 needs ~6 GB plus activations on CPU


def sh(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", **kw)


def avail_ram_gb() -> float:
    class MS(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
    try:
        m = MS(); m.dwLength = ctypes.sizeof(MS)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
        return m.ullAvailPhys / (1024 ** 3)
    except Exception:
        return 16.0


def ts_to_s(t: str) -> float:
    h, m, rest = t.split(":")
    s, ms = rest.split(",")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000.0


def s_to_ts(x: float) -> str:
    h = int(x // 3600); m = int((x % 3600) // 60); s = int(x % 60)
    return "%02d:%02d:%02d,%03d" % (h, m, s, round((x - int(x)) * 1000))


def detect_language(wav: str, use_cuda: bool = False) -> str:
    """Detect language once on the first 30s with tiny model."""
    lang = "en"
    try:
        from faster_whisper import WhisperModel
        device = "cuda" if use_cuda else "cpu"
        compute_type = "float16" if use_cuda else "int8"
        tm = WhisperModel("tiny", device=device, compute_type=compute_type)
        segments, info = tm.transcribe(wav, beam_size=1)
        lang = info.language
        top = sorted(info.all_language_probs, key=lambda kv: -kv[1])[:3] if info.all_language_probs else [(lang, info.language_probability)]
        print(f"[LANGUAGE] Detected '{lang}' (prob: {info.language_probability:.3f}) | top3: {top}", flush=True)
        del tm
    except Exception as e:
        print(f"[LANGUAGE] Warning: faster-whisper language detect fallback ({e}); trying vanilla whisper...", flush=True)
        try:
            import whisper
            tm = whisper.load_model("tiny")
            a = whisper.pad_or_trim(whisper.load_audio(wav))
            probs = tm.detect_language(whisper.log_mel_spectrogram(a).to(tm.device))[1]
            lang = max(probs, key=probs.get)
            top = sorted(probs.items(), key=lambda kv: -kv[1])[:3]
            print(f"[LANGUAGE] Detected '{lang}' | top3: {[(k, round(v, 3)) for k, v in top]}", flush=True)
            del tm
        except Exception as e2:
            print(f"[LANGUAGE] Detection failed ({e2}); forcing 'en'", flush=True)
            lang = "en"
    return lang


def transcribe_gpu(wav: str, lang: str, compute_type: str) -> list[tuple[float, float, str]] | None:
    """Attempt GPU transcription with faster-whisper on large-v3 with given compute_type."""
    try:
        from faster_whisper import WhisperModel
        print(f"[GPU] Loading {MODEL} on CUDA with compute_type={compute_type}...", flush=True)
        t0 = time.time()
        model = WhisperModel(MODEL, device="cuda", compute_type=compute_type)
        print(f"[GPU] Model loaded in {time.time() - t0:.2f}s. Starting transcription...", flush=True)
        
        t_trans = time.time()
        segments, info = model.transcribe(
            wav,
            language=lang,
            task="transcribe",
            beam_size=5,
            condition_on_previous_text=False,
            vad_filter=False
        )
        
        results = []
        for s in segments:
            results.append((s.start, s.end, s.text.strip()))
            
        print(f"[GPU] Completed {len(results)} segments in {time.time() - t_trans:.2f}s", flush=True)
        return results
    except Exception as e:
        print(f"[GPU] Transcription failed on CUDA with {compute_type}: {e}", flush=True)
        return None


def transcribe_cpu_chunked(wav: str, dur: float, lang: str, work: str) -> list[tuple[float, float, str]] | None:
    """Fallback CPU chunked parallel transcription using large-v3."""
    print("[CPU FALLBACK] Starting CPU chunked parallel transcription...", flush=True)
    cpus = os.cpu_count() or 8
    ram = avail_ram_gb()
    workers = max(1, min(8, int(ram // RAM_PER_WORKER_GB)))
    threads = max(2, cpus // workers)
    target = min(MAX_CHUNK, max(MIN_CHUNK, dur / workers))
    print(f"[CPU] duration {dur:.0f}s | RAM avail {ram:.0f}GB | {workers} workers x {threads} threads | ~{target:.0f}s chunks", flush=True)

    sil = [float(x) for x in re.findall(
        r"silence_start: ([0-9.]+)",
        sh(["ffmpeg", "-hide_banner", "-i", wav, "-af",
            "silencedetect=noise=-30dB:d=0.4", "-f", "null", "-"]).stderr)]
    print(f"[CPU] detected silences: {len(sil)}", flush=True)

    cuts = [0.0]
    while cuts[-1] + target < dur - 45:
        lo, hi = cuts[-1] + MIN_CHUNK, cuts[-1] + target * 1.7
        cand = [s for s in sil if lo < s < hi]
        cuts.append(round(min(cand, key=lambda s: abs(s - (cuts[-1] + target)))
                          if cand else cuts[-1] + target, 3))
    cuts.append(dur)
    spans = list(zip(cuts, cuts[1:]))
    print(f"[CPU] chunks: {len(spans)} {[round(b - a, 1) for a, b in spans]}", flush=True)

    for i, (a, b) in enumerate(spans):
        sh(["ffmpeg", "-y", "-loglevel", "error", "-ss", "%.3f" % a, "-to", "%.3f" % b,
            "-i", wav, "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le",
            os.path.join(work, "c%02d.wav" % i)])

    def run(i):
        env = dict(os.environ)
        env["OMP_NUM_THREADS"] = str(threads); env["MKL_NUM_THREADS"] = str(threads)
        r = sh(["whisper", os.path.join(work, "c%02d.wav" % i), "--model", MODEL,
                "--language", lang, "--task", "transcribe", "--output_dir", work,
                "--output_format", "srt", "--verbose", "False", "--fp16", "False",
                "--threads", str(threads)], env=env)
        ok = os.path.exists(os.path.join(work, "c%02d.srt" % i))
        print("  chunk %02d %s%s" % (i, "OK" if ok else "FAIL",
                                     "" if ok else " " + r.stderr[-300:]), flush=True)
        return ok

    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        results = list(ex.map(run, range(len(spans))))
    print("transcribed %d/%d chunks" % (sum(results), len(spans)), flush=True)

    parsed_segments = []
    for i, (a, _b) in enumerate(spans):
        f = os.path.join(work, "c%02d.srt" % i)
        if not os.path.exists(f):
            continue
        for blk in [x for x in open(f, encoding="utf-8").read().strip().split("\n\n") if x.strip()]:
            lines = blk.split("\n")
            if len(lines) < 3:
                continue
            st, en = [z.strip() for z in lines[1].split("-->")]
            text = " ".join(lines[2:]).strip()
            st_s, en_s = ts_to_s(st) + a, ts_to_s(en) + a
            parsed_segments.append((st_s, en_s, text))
    return parsed_segments


def main() -> int:
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        return 0
    src = os.path.abspath(sys.argv[1])

    if not os.path.exists(src):
        print("Not found: %s" % src)
        return 2
    stem = os.path.splitext(os.path.basename(src))[0]
    outdir = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else os.path.dirname(src)
    work = os.path.join(outdir, "_transcribe_%s" % re.sub(r"[^A-Za-z0-9_-]", "_", stem)[:40])
    os.makedirs(work, exist_ok=True)

    wav = os.path.join(work, "audio.wav")
    print(f"Extracting audio -> {wav}", flush=True)
    r = sh(["ffmpeg", "-y", "-loglevel", "error", "-i", src,
            "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", wav])
    if r.returncode != 0 or not os.path.exists(wav):
        print("ffmpeg failed:", r.stderr[-500:]); return 1

    dur = float(sh(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                    "-of", "csv=p=0", wav]).stdout.strip())

    # Check CUDA availability
    has_cuda = False
    try:
        import ctranslate2
        has_cuda = ctranslate2.get_cuda_device_count() > 0
    except Exception:
        pass

    lang = detect_language(wav, use_cuda=has_cuda)

    segments = None
    device_used = "cpu"
    precision_used = "fp32"
    backend_used = "whisper-cpu-chunked"

    if has_cuda:
        # Precision Ladder: Tier 1 (float16) -> Tier 2 (int8_float16)
        print("[HARDWARE] CUDA GPU detected. Engaging GPU pipeline...", flush=True)
        segments = transcribe_gpu(wav, lang, compute_type="float16")
        if segments is not None:
            device_used = "cuda:0"
            precision_used = "float16"
            backend_used = "faster-whisper (CTranslate2)"
        else:
            print("[FALLBACK] GPU float16 failed/OOM; attempting Tier 2: int8_float16...", flush=True)
            segments = transcribe_gpu(wav, lang, compute_type="int8_float16")
            if segments is not None:
                device_used = "cuda:0"
                precision_used = "int8_float16"
                backend_used = "faster-whisper (CTranslate2)"

    if segments is None:
        print("[FALLBACK] Engaging CPU chunked parallel fallback...", flush=True)
        segments = transcribe_cpu_chunked(wav, dur, lang, work)
        device_used = "cpu"
        precision_used = "fp32"
        backend_used = "openai-whisper (CPU parallel)"

    if not segments:
        print("[ERROR] Transcription failed completely.")
        return 1

    # Format SRT and TXT
    srt, txt, n = [], [], 1
    for st, en, text in segments:
        srt.append(f"{n}\n{s_to_ts(st)} --> {s_to_ts(en)}\n{text}\n")
        txt.append(f"[{s_to_ts(st)[:8]}] {text}")
        n += 1

    base = os.path.join(outdir, f"{stem}_large-v3")
    with open(base + ".srt", "w", encoding="utf-8") as f:
        f.write("\n".join(srt))
    with open(base + ".txt", "w", encoding="utf-8") as f:
        f.write("\n".join(txt))

    print(f"\n=======================================================")
    print(f"[SUMMARY] Execution Successful")
    print(f"  Model:      {MODEL} (Hard project rule: large-v3 only)")
    print(f"  Backend:    {backend_used}")
    print(f"  Device:     {device_used}")
    print(f"  Precision:  {precision_used}")
    print(f"  Language:   {lang}")
    print(f"  Duration:   {dur:.1f}s ({dur/60:.2f} min)")
    print(f"  Wrote:      {base}.txt ({len(txt)} lines, {sum(len(l.split()) for l in txt)} words)")
    print(f"  Wrote:      {base}.srt")
    print(f"=======================================================\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
