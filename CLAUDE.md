# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

MediaMarauder is a Dockerized video downloader system with a Flask backend that processes URLs submitted via a Chrome extension. It uses yt-dlp to download videos from supported platforms with optional subtitle support, Google OAuth authentication, queue-based processing, and real-time progress tracking with a modern web UI.

## Architecture

### Core Components

1. **app.py** - Flask application entry point
   - Initializes the Downloader class and authentication
   - Routes: `/` (loader), `/landing`, `/{WEBHOOK_PATH}` (add downloads), `/{STATUS_PATH}` (queue status), `/status-page` (UI)
   - Automatically starts queue processor in background thread on startup

2. **download.py** - Download queue manager and processor
   - `Downloader` class handles queue operations with thread-safe locking
   - `process_queue()` runs in daemon thread, continuously polling for URLs every 5 seconds
   - `download_file()` executes yt-dlp subprocess with stderr redirected to stdout (critical for preventing blocking on large files)
   - Tracks current download percentage by parsing yt-dlp output with regex
   - Supports subtitle downloads with `--write-subs` and language specification

3. **auth.py** - Google OAuth integration
   - Uses Authlib for OAuth flow
   - Restricts access to single email address via `ALLOWED_EMAIL` config
   - Provides `@login_required` decorator for protected routes
   - Routes: `/login`, `/auth` (OAuth callback), `/logout`

4. **securityUtils.py** - URL validation and security
   - Validates URLs against `WHITELISTED_DOMAINS` from config
   - Checks for malicious characters (`;`, `|`, `&&`)
   - Prevents directory traversal attacks
   - Sanitizes filenames to remove dangerous characters

5. **config.py** - Configuration (not in repo, see config_example.py)
   - `DOWNLOAD_PATH` - where videos are saved
   - `WEBHOOK_PATH` and `STATUS_PATH` - custom endpoint paths
   - `WHITELISTED_DOMAINS` - allowed video platforms
   - `API_TOKENS` - authentication for webhook endpoint
   - `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `ALLOWED_EMAIL` - OAuth settings

6. **templates/status.html** - Real-time status dashboard
   - Modern card-based UI with responsive design
   - Live progress bar with percentage tracking (updates every second)
   - Animated "✓ Complete!" indicator when downloads finish
   - XSS-protected using `escapeHtml()` function for all dynamic content
   - Auto-hides progress section when idle or after completion

### Critical Implementation Details

**Subprocess Blocking Fix (download.py:151)**
The yt-dlp subprocess redirects stderr to stdout (`stderr=subprocess.STDOUT`) to prevent blocking on large downloads. Without this, the stderr buffer fills when yt-dlp writes warnings/errors, causing the process to hang indefinitely. This was a critical bug fix for downloads >1GB.

**Queue Processing Thread (app.py:99-106)**
Queue processor starts automatically on app startup as a daemon thread. This ensures downloads continue processing without manual intervention. The thread polls the queue every 5 seconds when empty, processes immediately when URLs are available.

**Thread Safety**
The Downloader class uses `threading.Lock()` to protect shared state (`url_queue`, `downloaded_files`, `current_download_status`, `current_download_percentage`). All methods that read/write these use `with self.lock:` context managers.

**Progress Bar Reset (download.py:218-220)**
After each download completes, `current_download_percentage` is reset to 0. This ensures the progress bar section auto-hides on the status page, providing clean UX where the progress only shows during active downloads.

## Development Commands

### Local Development
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application (starts on port 5000)
python app.py
```

### Docker
```bash
# Build image
docker build -t mediamarauder .

# Run container
docker run -d --name mediamarauder --restart unless-stopped \
    -p 5000:5000 \
    -v /path/to/downloads:/app/downloads \
    -v /path/to/config.py:/app/config.py \
    mathin/mediamarauder:latest
```

### Testing
No formal test suite exists. Manual testing workflow:
1. Start app locally: `python app.py`
2. Submit URL via Chrome extension or curl to webhook endpoint
3. Monitor queue via status endpoint or status-page UI
4. Verify downloads appear in configured DOWNLOAD_PATH

## Configuration Requirements

Before running, create `config.py` based on `config_example.py`:
- Set `DOWNLOAD_PATH` to absolute path for video storage
- Configure Google OAuth credentials from Google Cloud Console
- Add authorized redirect URIs: `http://localhost:5000/auth` and production domain
- Whitelist video platform domains in `WHITELISTED_DOMAINS`
- Generate secure API tokens for Chrome extension authentication

## Dependencies

Key Python packages (requirements.txt):
- Flask 2.2.5 (web framework, pinned for Authlib compatibility)
- yt-dlp (video downloading)
- Authlib 1.6.5 (Google OAuth)
- werkzeug >=3.1.4 (security patches for CVE-2025-66221)
- urllib3 >=2.6.0 (security patches for CVE-2025-66471, CVE-2025-66418)

System dependencies (installed in Dockerfile):
- ffmpeg (video transcoding for `--recode-video mp4`)
- yt-dlp binary (latest release from GitHub)

## Chrome Extension Integration

The extension (ChromeExtension/) sends POST requests to the webhook endpoint with:
- Header: `Auth: {API_TOKEN}`
- Body: `{"url": "video_url", "subtitle_lang": "en"}` (subtitle_lang optional)

Authentication uses API tokens from config, separate from Google OAuth (which is for web UI access only).
