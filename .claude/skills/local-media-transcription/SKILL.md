---
name: local-media-transcription
description: Transcribe local audio and video files using whisper large-v3 on the local NVIDIA RTX A5000 GPU with automatic fallback ladder (cuda/float16 -> cuda/int8_float16 -> cpu chunked). Outputs timestamped .txt and .srt files locally with zero cloud leakage.
---

# Local Media Transcription (GPU-First)

Use this skill whenever you need to transcribe audio or video recordings (e.g. meeting recordings, interviews, technical presentations, internal calls) in any project on this machine.

---

## Standing Rules & Constraints

1. **GPU-First (NVIDIA RTX A5000):** Always execute transcription on CUDA via `faster-whisper` (CTranslate2).
2. **Model Constraint:** Always use **`large-v3`** (32 layers). Never substitute `turbo`, `small`, `base`, or `medium`. Proper-noun fidelity (*vendor names, model names, people*) is mandatory.
3. **100% Local & Confidential:** No audio, video, or transcripts may be sent to any external service or API.
4. **Precision Fallback Ladder:**
   - **Tier 1:** CUDA `float16` (Default, ~4.0 GB VRAM, ~5x real-time speedup)
   - **Tier 2:** CUDA `int8_float16` (Fallback on VRAM pressure, ~2.8 GB VRAM)
   - **Tier 3:** CPU chunked parallel (Emergency fallback if CUDA is unavailable)

---

## How to Transcribe

Run the bundled transcription script on your target media file:

```powershell
python .agents/skills/local-media-transcription/scripts/transcribe.py "<media-file>" [output-dir]
```

Or pass the direct path:
```powershell
python scripts/transcribe_local_large_v3.py "<media-file>" [output-dir]
```

### Outputs
- `<output-dir>/<stem>_large-v3.txt` (Timestamped format: `[HH:MM:SS] text`)
- `<output-dir>/<stem>_large-v3.srt` (Standard SRT subtitle format with millisecond precision)

---

## Technical Details

- **Language Detection:** Detects language once on the first 30 seconds using `tiny` and forces the detected language on `large-v3` to prevent per-segment mis-detection.
- **Audio Extraction:** Uses `ffmpeg -vn -ac 1 -ar 16000 -c:a pcm_s16le` for clean 16kHz mono audio.
- **Speech Conditioning:** Sets `condition_on_previous_text=False` and `vad_filter=False` to prevent clipping quiet words or hallucinating across silence boundaries.
