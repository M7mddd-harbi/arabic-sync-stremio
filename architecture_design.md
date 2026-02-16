# Arabic Auto-Sync Subtitles Addon: Technical Architecture

The Arabic Auto-Sync Subtitles Addon is designed as a modular Stremio addon that leverages advanced audio fingerprinting and synchronization engines to provide perfectly timed Arabic subtitles. The system consists of four primary components: the **Addon Interface**, the **Sync Engine**, the **Storage & Caching Layer**, and the **Proxy Server**.

### Component Overview

| Component | Responsibility | Technology |
| :--- | :--- | :--- |
| **Addon Interface** | Handles Stremio protocol requests and serves the manifest. | Node.js / Express / Stremio SDK |
| **Sync Engine** | Performs audio-to-subtitle alignment and text normalization. | Python / FFsubsync / ALASS |
| **Storage Layer** | Caches synced subtitles and manages processing states. | SQLite / File System |
| **Proxy Server** | Serves processed SRT files and handles local file uploads. | Express Static / Multer |

### Data Flow and Processing Strategy

When a user selects a video in Stremio, the addon receives a subtitle request. If a synced version is already in the **Smart Cache**, the addon returns the URL immediately. If not, the system initiates an **Anti-Timeout Strategy** by returning a placeholder subtitle that informs the user the sync is in progress. 

Simultaneously, a background worker triggers the **Sync Engine**. This engine downloads the reference audio (or uses the stream URL), fetches the original Arabic subtitle, and applies **FFsubsync** or **ALASS** for alignment. Before final delivery, the subtitle undergoes **Arabic Text Normalization**, which removes diacritics and fixes common formatting issues to ensure maximum readability.

### Local File Support

To support local SRT files, the addon provides a simple web-based upload interface. Once a file is uploaded, it is assigned a unique ID and processed through the same synchronization pipeline, allowing users to align their own local files with the streaming content effortlessly.
