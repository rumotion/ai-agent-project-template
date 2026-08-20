---
name: sharepoint-teams-video-transcript-downloader
description: Automated tool and workflow to extract, download, and format 100% full-length Microsoft Teams / SharePoint Stream video recordings (1080p MP4 at strict 1.0x native normal playback speed) and complete speaker-annotated transcripts (.txt and .srt) without missing virtualized cues or playing audio.
---

# SharePoint / Teams Video & Transcript Downloader

Use this skill when a user wants to download a Microsoft Teams meeting recording or video hosted on SharePoint / Stream, along with its complete, full-length speaker-annotated transcript and subtitles.

---

## Technical Overview & Solutions Solved

1. **Authentication & Session Persistence:**
   - Stream requires SharePoint session authentication (`rtFa` and `FedAuth` Netscape cookies) or Chrome CDP / Playwright context.
2. **Lossless Video Download & Playback Speed Preservation:**
   - When direct download buttons are disabled or DASH manifests (`videomanifest?provider=spo...`) use DRM / 12-second token expirations, direct segment concatenation can fail or require decryption.
   - **Automated Fallback:** Uses a headless Playwright Chromium browser context with `MediaRecorder` (`video.captureStream()`).
   - **CRITICAL SPEED REQUIREMENT:** Playback rate MUST be set to **STRICT 1.0x native normal speed** (`v.playbackRate = 1.0;`). Setting `playbackRate > 1.0` (e.g. 4x or 16x) causes the output stream to encode at accelerated playback rates, making the resulting video play back in fast-forward!
   - Chunks are streamed incrementally to disk every 5 seconds to prevent browser memory exhaustion on long recordings.
   - Converted to `.mp4` container via `ffmpeg -i temp.webm -c:v copy -c:a copy output.mp4`.
3. **Complete 100% Transcript Extraction (No Missing Cues):**
   - Direct GET requests to `/_api_cached/v2.1/.../cdnmedia/transcripts` return raw compressed Brotli stream bytes (`b'B\x1c'`) which fail plain text decoding.
   - Microsoft Stream renders transcript cues inside a virtualized Fluent UI container (`.ms-FocusZone` / `div` with `scrollHeight > 5000px`) that unmounts offscreen DOM nodes as you scroll.
   - **Solution:** Automated Playwright browser context in **MUTED MODE** (`--mute-audio` flag) that navigates to the video page, opens the Transcript side panel, and programmatically scrolls down the virtualized container from `0px` to max height (`~60,000px`), harvesting 100% of speaker cues and timestamps.

---

## Step-by-Step Execution Workflow

### Step 1: Prerequisites Check

Ensure Python environment has required packages installed:
```powershell
pip install yt-dlp playwright
playwright install chromium
```

Ensure `ffmpeg` is available on system `PATH`.

---

### Step 2: Export Session Cookies

Export active SharePoint session cookies into Netscape format (`sp_session_cookies.txt`):
- Extract via Playwright context / Chrome CDP (`rtFa`, `FedAuth` cookies) or browser extension.

---

### Step 3: Automated Video Download

Run the bundled video downloader script (`scripts/download_sharepoint_stream.py`):

```powershell
python scripts/download_sharepoint_stream.py --url "<SHAREPOINT_STREAM_URL>" --cookies "sp_session_cookies.txt" --out "Meeting Recording.mp4"
```

#### What the Script Does Automatically:
1. Tries direct `yt-dlp` download with Netscape session cookies.
2. If direct download is restricted (no download button / token timeout / DRM):
   - Launches Playwright Chromium with Netscape cookies in muted mode (`--mute-audio`).
   - Sets `<video>` playback rate to **STRICT 1.0x native normal speed** (`v.playbackRate = 1.0`).
   - Captures decoded 1080p video/audio stream via HTML5 `MediaRecorder`.
   - Streams chunks incrementally to disk every 5 seconds (`temp_stream_recorded_1x.webm`).
   - Converts the stream to final `.mp4` container using `ffmpeg`.
   - Cleans up temporary `.webm` files upon completion.

---

### Step 4: Harvest 100% Full Transcript & SRT Subtitles

Run the automated Playwright harvester script (`scripts/harvest_sharepoint_transcript.py`):

```powershell
python scripts/harvest_sharepoint_transcript.py --url "<SHAREPOINT_STREAM_URL>" --cookies "sp_session_cookies.txt" --out-dir "<DESTINATION_DIR>"
```

#### Outputs Formatted Files:
- `[Title] - Complete Transcript.txt` (Clean dialogue tagged with speaker names and timestamps)
- `[Title] - Complete.srt` (Valid SRT subtitle file)

---

## Troubleshooting & Edge Cases

| Issue | Root Cause | Solution |
| :--- | :--- | :--- |
| **Downloaded video plays in fast-forward / sped up** | `playbackRate` was set > 1.0 (e.g. 4.0 or 16.0) during `MediaRecorder` stream capture. | Always set `v.playbackRate = 1.0` (strict native normal speed) in `MediaRecorder` capture. |
| **Direct GET transcript returns garbage text** | Direct API endpoint returns compressed Brotli binary stream. | Use Playwright DOM harvesting script (`harvest_sharepoint_transcript.py`). |
| **Only 10-15 minutes of transcript saved** | Stream list is virtualized; un-scrolled DOM nodes aren't rendered. | Script performs step-by-step scrolling (`scrollTop += 400`) until bottom reached. |
| **Audio playing during harvest** | Default browser playback triggers audio on load. | Always pass `--mute-audio` in Chromium launch args and pause `<video>` via DOM evaluate. |

---

## Bundled Helper Scripts

1. `scripts/download_sharepoint_stream.py` - Automated video downloader with 1.0x native speed MediaRecorder fallback.
2. `scripts/harvest_sharepoint_transcript.py` - Complete 100% transcript harvester.
