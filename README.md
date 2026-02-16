# Arabic Auto-Sync Subtitles Addon for Stremio

An advanced Stremio addon that provides perfectly synchronized Arabic subtitles using audio fingerprinting and smart alignment.

## Features

- **Zero-Delay Sync**: Uses `FFsubsync` to align subtitles with the actual audio track of the video.
- **Arabic Text Normalization**: Automatically removes diacritics (Tashkeel) and normalizes Arabic characters for better readability.
- **Smart Caching**: Once a subtitle is synced for a specific media ID, it's served instantly to all future users.
- **Anti-Timeout Strategy**: Returns a placeholder "Processing..." subtitle immediately so Stremio doesn't time out while the sync engine works in the background.
- **Local File Support**: Allows users to upload their own SRT files to be synced with the stream.

## Installation

1. **Open Stremio**.
2. Go to the **Addons** section.
3. Click on **Add community addon**.
4. Paste the following URL:
   `http://your-server-ip:7000/manifest.json`
5. Click **Install**.

## Technical Setup (Self-Hosting)

### Prerequisites
- Node.js (v18+)
- Python 3.11+
- FFmpeg

### Steps
1. Clone the repository.
2. Install Node.js dependencies:
   ```bash
   pnpm install
   ```
3. Install Python dependencies:
   ```bash
   sudo apt-get install build-essential python3-dev ffmpeg
   pip3 install ffsubsync
   ```
4. Start the server:
   ```bash
   node server.js
   ```

## How it Works
1. When you play a video, Stremio requests subtitles from this addon.
2. The addon checks if a synced version exists in the `cache/` directory.
3. If not, it returns a placeholder subtitle and starts a background process:
   - Downloads the original Arabic SRT.
   - Runs `ffsubsync` against the video stream's audio.
   - Normalizes the Arabic text.
   - Saves the result to cache.
4. On the next refresh (or after a few seconds), the perfectly synced subtitle is served.
