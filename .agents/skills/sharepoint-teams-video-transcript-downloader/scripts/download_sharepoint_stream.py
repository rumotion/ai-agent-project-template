import sys
import os
import time
import base64
import argparse
import subprocess
from playwright.sync_api import sync_playwright

def load_netscape_cookies(cookie_file):
    cookies = []
    if not os.path.exists(cookie_file):
        return cookies
    with open(cookie_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.strip().split("\t")
            if len(parts) >= 7:
                cookies.append({
                    "domain": parts[0],
                    "path": parts[2],
                    "secure": parts[3].upper() == "TRUE",
                    "name": parts[5],
                    "value": parts[6]
                })
    return cookies

def try_ytdlp_download(url, cookie_file, out_path):
    print("[*] Attempting direct download via yt-dlp...")
    cmd = [
        "yt-dlp",
        "--cookies", cookie_file,
        "--referer", "https://sharepoint.com",
        "-f", "dash-vcopy+dash-audcopy",
        "--merge-output-format", "mp4",
        "-o", out_path,
        url
    ]
    res = subprocess.run(cmd)
    return res.returncode == 0 and os.path.exists(out_path) and os.path.getsize(out_path) > 1000000

def record_stream_playwright_1x(url, cookie_file, out_path):
    print("[*] Falling back to automated Playwright MediaRecorder at STRICT 1.0x native normal playback speed...")
    out_dir = os.path.dirname(os.path.abspath(out_path)) or "."
    recorded_webm = os.path.join(out_dir, "temp_stream_recorded_1x.webm")

    if os.path.exists(recorded_webm):
        try: os.remove(recorded_webm)
        except Exception: pass

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--mute-audio", "--autoplay-policy=no-user-gesture-required"])
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        
        cookies = load_netscape_cookies(cookie_file)
        if cookies:
            context.add_cookies(cookies)

        page = context.new_page()

        print("[*] Loading Stream player page...")
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
        except Exception:
            pass

        time.sleep(6)

        print("[*] Injecting MediaRecorder at 1.0x native normal playback speed...")
        page.evaluate("""() => {
            window._pendingChunks = [];
            window._recFinished = false;

            const v = document.querySelector('video');
            if (!v) return;

            v.muted = true;
            v.playbackRate = 1.0; // STRICT 1.0x NATIVE NORMAL SPEED
            v.currentTime = 0;

            const stream = v.captureStream ? v.captureStream() : v.mozCaptureStream();
            const recorder = new MediaRecorder(stream, { mimeType: 'video/webm;codecs=vp9,opus' });

            recorder.ondataavailable = async (e) => {
                if (e.data && e.data.size > 0) {
                    const buffer = await e.data.arrayBuffer();
                    const bytes = new Uint8Array(buffer);
                    let binary = '';
                    for (let i = 0; i < bytes.byteLength; i++) {
                        binary += String.fromCharCode(bytes[i]);
                    }
                    window._pendingChunks.push(btoa(binary));
                }
            };

            window._recorder = recorder;
            recorder.start(1000); // 1s slice
            v.play().catch(e => {});

            v.onended = () => {
                recorder.stop();
                window._recFinished = true;
            };
        }""")

        f_out = open(recorded_webm, "wb")
        total_bytes = 0

        # Max recording budget: 3600 seconds (1 hour)
        max_loops = 720
        for loop in range(max_loops):
            time.sleep(5)
            chunks = page.evaluate("""() => {
                const c = window._pendingChunks || [];
                window._pendingChunks = [];
                const v = document.querySelector('video');
                return {
                    chunks: c,
                    cur: v ? v.currentTime : 0,
                    dur: v ? v.duration : 1,
                    ended: v ? v.ended : false,
                    paused: v ? v.paused : false
                };
            }""")
            
            for b64 in chunks.get("chunks", []):
                raw = base64.b64decode(b64)
                f_out.write(raw)
                total_bytes += len(raw)

            cur = chunks.get("cur", 0)
            dur = chunks.get("dur", 1)
            pct = (cur / dur * 100) if dur else 0
            print(f"  [1.0x Speed Recording] {cur:.1f}s / {dur:.1f}s ({pct:.1f}%) | Disk written: {total_bytes/(1024*1024):.2f} MB")

            if chunks.get("ended") or (dur > 10 and cur >= (dur - 1)):
                print("[+] Playback completed naturally!")
                break

            if chunks.get("paused"):
                page.evaluate("() => { const v = document.querySelector('video'); if (v) v.play().catch(e => {}); }")

        page.evaluate("() => { if (window._recorder && window._recorder.state !== 'inactive') window._recorder.stop(); }")
        time.sleep(1)
        f_out.close()
        browser.close()

    if os.path.exists(recorded_webm) and os.path.getsize(recorded_webm) > 1000000:
        print("[*] Converting WebM stream to final 1080p MP4 container via ffmpeg...")
        ffmpeg_cmd = [
            "ffmpeg", "-y",
            "-i", recorded_webm,
            "-c:v", "copy",
            "-c:a", "copy",
            out_path
        ]
        res_ff = subprocess.run(ffmpeg_cmd)

        if res_ff.returncode == 0 and os.path.exists(out_path):
            size_mb = os.path.getsize(out_path) / (1024 * 1024)
            print(f"[SUCCESS] 1.0x Native Speed MP4 created at {out_path} ({size_mb:.2f} MB)")
            try: os.remove(recorded_webm)
            except Exception: pass
            return True

    print("[-] Automated MediaRecorder capture failed.")
    return False

def main():
    parser = argparse.ArgumentParser(description="Automated SharePoint Stream Video Downloader")
    parser.add_argument("--url", required=True, help="SharePoint Stream web URL or videomanifest URL")
    parser.add_argument("--cookies", required=True, help="Path to Netscape cookies text file")
    parser.add_argument("--out", default="SharePoint_Video.mp4", help="Output MP4 file path")
    args = parser.parse_args()

    print(f"[*] Target URL: {args.url}")
    print(f"[*] Cookie File: {args.cookies}")
    print(f"[*] Output Target: {args.out}")

    # 1. Try yt-dlp direct download
    if try_ytdlp_download(args.url, args.cookies, args.out):
        print(f"[SUCCESS] Direct yt-dlp download completed!")
        return

    # 2. Automated fallback to Playwright MediaRecorder at 1.0x native normal speed
    if record_stream_playwright_1x(args.url, args.cookies, args.out):
        print(f"[SUCCESS] Automated 1.0x speed video capture completed!")
        return

    print("[-] All download methods failed.")
    sys.exit(1)

if __name__ == "__main__":
    main()
