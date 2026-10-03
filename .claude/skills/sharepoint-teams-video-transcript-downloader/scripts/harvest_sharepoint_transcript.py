import sys
import os
import json
import re
import time
import argparse
from playwright.sync_api import sync_playwright

KNOWN_SPEAKERS = [
    "Alex Morin", "Nathaniel Larouche", "Bryan Howard", "Asad Manzoor",
    "Simone Rizzo", "Sergei Sarichev", "Joe R", "Mike L", "Victor", "Goran", "Andre", "Zach Dembinski"
]

def clean_line(l):
    l = re.sub(r'[\ue000-\uf8ff]', '', l).strip()
    l = re.sub(r'^\s*\d+\s*hours?\s*', '', l, flags=re.I)
    l = re.sub(r'^\s*\d+\s*minutes?\s*\d*\s*seconds?\s*', '', l, flags=re.I)
    l = re.sub(r'\b1\s*hour\b', '', l, flags=re.I)
    l = re.sub(r'Started transcription', '', l, flags=re.I)
    l = re.sub(r'Stopped transcription', '', l, flags=re.I)
    return l.strip()

def convert_time_to_srt(time_str):
    m = re.search(r'(?:(\d+):)?(\d+):(\d+)', time_str)
    if m:
        hrs = int(m.group(1)) if m.group(1) else 0
        mins = int(m.group(2))
        secs = int(m.group(3))
    else:
        m2 = re.search(r'(\d+):(\d+)', time_str)
        if m2:
            hrs = 0
            mins = int(m2.group(1))
            secs = int(m2.group(2))
        else:
            return "00:00:00,000"
    return f"{hrs:02d}:{mins:02d}:{secs:02d},000"

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
                c = {
                    "domain": parts[0],
                    "path": parts[2],
                    "secure": parts[3].upper() == "TRUE",
                    "name": parts[5],
                    "value": parts[6]
                }
                cookies.append(c)
    return cookies

def main():
    parser = argparse.ArgumentParser(description="Harvest 100% full-length transcript & SRT from SharePoint Stream")
    parser.add_argument("--url", required=True, help="SharePoint Stream web URL")
    parser.add_argument("--cookies", required=True, help="Path to Netscape cookies text file")
    parser.add_argument("--out-dir", default=".", help="Directory to save transcript .txt and .srt files")
    parser.add_argument("--title", default="SharePoint_Meeting", help="Title prefix for output files")
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    print("[*] Launching MUTED Chromium browser instance...")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--mute-audio", "--autoplay-policy=no-user-gesture-required"]
        )
        context = browser.new_context(viewport={"width": 1280, "height": 900})

        cookies = load_netscape_cookies(args.cookies)
        if cookies:
            context.add_cookies(cookies)
            print(f"[+] Loaded {len(cookies)} authentication cookies into browser context.")

        page = context.new_page()
        print(f"[*] Navigating to SharePoint Stream page (Muted Audio)...")
        page.goto(args.url, wait_until="domcontentloaded", timeout=90000)
        time.sleep(5)

        # Pause and mute video element
        page.evaluate("""
        () => {
            const v = document.querySelector('video');
            if (v) {
                v.muted = true;
                v.pause();
            }
        }
        """)

        # Open Transcript panel
        print("[*] Opening Transcript side panel...")
        page.evaluate("""
        () => {
            const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText && b.innerText.includes('Transcript'));
            if (btn) btn.click();
        }
        """)
        time.sleep(3)

        # Find virtualized scroll container (> 5000px height)
        js_find_container = """
        () => {
            const el = Array.from(document.querySelectorAll('div')).find(e => e.scrollHeight > 5000);
            if (el) {
                el.scrollTop = 0;
                return {
                    scrollHeight: el.scrollHeight,
                    clientHeight: el.clientHeight,
                    className: el.className
                };
            }
            return null;
        }
        """

        scroll_info = page.evaluate(js_find_container)
        if not scroll_info:
            time.sleep(3)
            scroll_info = page.evaluate(js_find_container)

        if not scroll_info:
            print("[-] Could not locate virtualized transcript container >5000px.")
            browser.close()
            return

        total_height = scroll_info["scrollHeight"]
        print(f"[+] Found Transcript Scroll Container! Height: {total_height} px")

        harvested_cues = []
        seen_texts = set()

        js_harvest = """
        () => {
            const items = [];
            const nodes = document.querySelectorAll('[role="listitem"], [data-automation-id*="cue"]');
            nodes.forEach(n => {
                const t = n.innerText ? n.innerText.trim() : '';
                if (t) items.push(t);
            });
            return items;
        }
        """

        js_scroll_step = """
        (stepPx) => {
            const el = Array.from(document.querySelectorAll('div')).find(e => e.scrollHeight > 5000);
            if (el) {
                const old = el.scrollTop;
                el.scrollTop += stepPx;
                return {
                    scrollTop: el.scrollTop,
                    scrollHeight: el.scrollHeight,
                    moved: el.scrollTop > old
                };
            }
            return { scrollTop: 0, scrollHeight: 0, moved: false };
        }
        """

        step_size = 400
        consecutive_stuck = 0
        current_pos = 0
        step_idx = 0

        print(f"[*] Starting full transcript harvest (0 px -> {total_height} px)...")

        while current_pos < total_height + 2000:
            cues_now = page.evaluate(js_harvest)
            for c in cues_now:
                if c not in seen_texts:
                    seen_texts.add(c)
                    harvested_cues.append(c)

            res = page.evaluate(js_scroll_step, step_size)
            current_pos = res["scrollTop"]

            if step_idx % 25 == 0:
                pct = (current_pos / total_height) * 100 if total_height > 0 else 0
                print(f"   Progress: {current_pos:5d} / {total_height:5d} px ({pct:5.1f}%) | Unique Cues: {len(harvested_cues)}")

            if not res["moved"]:
                consecutive_stuck += 1
                if consecutive_stuck >= 12:
                    print(f"[+] Reached 100% bottom of transcript scroll container at {current_pos} px!")
                    break
            else:
                consecutive_stuck = 0

            time.sleep(0.18)
            step_idx += 1

        # Final pass
        cues_now = page.evaluate(js_harvest)
        for c in cues_now:
            if c not in seen_texts:
                seen_texts.add(c)
                harvested_cues.append(c)

        print(f"\n[+] Total unique raw cues harvested: {len(harvested_cues)}")
        browser.close()

        # Parse cues into clean speaker turns
        parsed_entries = []
        curr_speaker = "Unknown Speaker"
        curr_time = "0:00"

        for raw_text in harvested_cues:
            lines = [clean_line(l) for l in raw_text.splitlines() if clean_line(l)]
            if not lines:
                continue

            speech_parts = []

            for l in lines:
                if l in ["Transcript", "Download", "Search", "Close", "AI-generated content may be incorrect"]:
                    continue
                if "permission" in l or "arrow keys" in l:
                    continue

                tm = re.search(r'\b(\d{1,2}:\d{2}(?::\d{2})?)\b', l)
                if tm and not speech_parts:
                    curr_time = tm.group(1)
                    spk_candidate = l.split(curr_time)[0].strip()
                    for s in KNOWN_SPEAKERS:
                        if s.lower() in spk_candidate.lower():
                            curr_speaker = s
                            break
                    continue

                matched_spk = None
                for s in KNOWN_SPEAKERS:
                    if s.lower() in l.lower():
                        matched_spk = s
                        break

                if matched_spk:
                    curr_speaker = matched_spk
                    continue

                if re.match(r'^[A-Z]{2}$', l):
                    continue

                speech_parts.append(l)

            if speech_parts:
                parsed_entries.append({
                    "speaker": curr_speaker,
                    "time": curr_time,
                    "text": " ".join(speech_parts)
                })

        # Consolidate consecutive entries from same speaker
        consolidated = []
        for entry in parsed_entries:
            if consolidated and consolidated[-1]["speaker"] == entry["speaker"] and entry["speaker"] != "Unknown Speaker":
                if entry["text"] not in consolidated[-1]["text"]:
                    consolidated[-1]["text"] += " " + entry["text"]
            else:
                consolidated.append(entry.copy())

        txt_file = os.path.join(args.out_dir, f"{args.title} - Complete Transcript.txt")
        srt_file = os.path.join(args.out_dir, f"{args.title} - Complete.srt")

        with open(txt_file, "w", encoding="utf-8") as f:
            f.write("========================================================================\n")
            f.write(f" FULL MEETING TRANSCRIPT: {args.title}\n")
            f.write(f" Total Speaker Turns Harvested: {len(consolidated)}\n")
            f.write("========================================================================\n\n")
            for entry in consolidated:
                f.write(f"[{entry['time']}] {entry['speaker']}:\n  {entry['text']}\n\n")

        print(f"[SUCCESS] Saved Complete Transcript ({len(consolidated)} turns) to:\n  {txt_file}")

        with open(srt_file, "w", encoding="utf-8") as f:
            for idx, entry in enumerate(consolidated, 1):
                start_srt = convert_time_to_srt(entry["time"])
                if idx < len(consolidated):
                    end_srt = convert_time_to_srt(consolidated[idx]["time"])
                else:
                    end_srt = convert_time_to_srt(entry["time"])

                f.write(f"{idx}\n")
                f.write(f"{start_srt} --> {end_srt}\n")
                f.write(f"[{entry['speaker']}]: {entry['text']}\n\n")

        print(f"[SUCCESS] Saved SRT Subtitles to:\n  {srt_file}")

if __name__ == "__main__":
    main()
