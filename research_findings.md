# Arabic Auto-Sync Subtitles Addon Research Findings

## Stremio Addon Protocol
- **Manifest**: Requires `subtitles` resource and `idPrefixes` (e.g., `tt` for IMDb).
- **Subtitles Object**:
    - `id`: Unique identifier.
    - `url`: URL to the SRT/VTT file.
    - `lang`: Language code (ISO 639-2, e.g., `ara` for Arabic).
- **Endpoint**: `GET /subtitles/{type}/{id}/{extra}.json`.
- **Placeholder Strategy**: Can return a "Processing..." subtitle URL immediately while background task syncs.

## Synchronization Tools
- **FFsubsync**: 
    - Can be used as a library or CLI.
    - Aligns subtitles with audio or other subtitles.
    - Command: `ffsubsync video.mp4 -i unsynced.srt -o synced.srt`.
- **ALASS**:
    - Rust-based, very fast.
    - Handles constant offsets and splits (commercials).
    - Command: `alass reference.mp4 unsynced.srt synced.srt`.

## Arabic Text Normalization
- Remove diacritics (Tashkeel).
- Normalize Alef, Yeh, Te Marbuta.
- Python `unicodedata` and `re` can handle this.

## Caching & Performance
- Use SQLite or Redis for caching synced SRT URLs or content.
- Need a proxy server to serve the synced SRT files.

## Local File Support
- Stremio's "Local Files" addon handles local media.
- For local SRT, the addon can provide an upload endpoint or use a local path if the addon runs locally.
