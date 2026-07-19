A Dockerized video downloader system for offline viewing that processes URLs submitted via a Chrome extension. It downloads videos from supported platforms (using yt-dlp) with options for subtitles, using a Flask-based backend. The system features queue management, authentication (Google OAuth), and organized storage.
```
███╗   ███╗███████╗██████╗ ██╗ █████╗ 
████╗ ████║██╔════╝██╔══██╗██║██╔══██╗
██╔████╔██║█████╗  ██║  ██║██║███████║
██║╚██╔╝██║██╔══╝  ██║  ██║██║██╔══██║
██║ ╚═╝ ██║███████╗██████╔╝██║██║  ██║
╚═╝     ╚═╝╚══════╝╚═════╝ ╚═╝╚═╝  ╚═╝
                                      
███╗   ███╗ █████╗ ██████╗  █████╗ ██╗   ██╗██████╗ ███████╗██████╗ 
████╗ ████║██╔══██╗██╔══██╗██╔══██╗██║   ██║██╔══██╗██╔════╝██╔══██╗
██╔████╔██║███████║██████╔╝███████║██║   ██║██║  ██║█████╗  ██████╔╝
██║╚██╔╝██║██╔══██║██╔══██╗██╔══██║██║   ██║██║  ██║██╔══╝  ██╔══██╗
██║ ╚═╝ ██║██║  ██║██║  ██║██║  ██║╚██████╔╝██████╔╝███████╗██║  ██║
╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝
```

## Features
- Secure Google OAuth authentication
- Download queue management
- Real-time status monitoring
- Subtitle download support
- Automated queue processing
- Chrome extension support
- Docker deployment with volume mounting
- HTTPS security via Caddy (recommended)

## Prerequisites
- Python 3.9 or higher
- Docker (recommended)
- A Google Cloud Platform account
- ffmpeg
- yt-dlp
- Chrome browser (for extension)

## Setup

### 1. Google OAuth Configuration
1. Go to the [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select an existing one
3. Enable the Google OAuth API
4. Go to "APIs & Services" → "Credentials"
5. Create OAuth 2.0 Client ID credentials for a "Web application"
6. Add authorized redirect URIs:
   - `http://localhost:5000/auth`
   - `http://127.0.0.1:5000/auth`
   - Add your production domain: `https://yourdomain.com/auth`

### 2. Configuration Setup
Create `config.py`:
```python
DOWNLOAD_PATH = "/app/downloads"
WEBHOOK_PATH = "/your-webhook-path"
STATUS_PATH = "/your-status-path"
WHITELISTED_DOMAINS = [
    "video-service.domain",
    "another-video-service.domain"
]
API_TOKENS = {
    "user": "your-api-token"
}

# Flask session secret key -- generate with: python -c "import os; print(os.urandom(24).hex())"
SECRET_KEY = "your-secret-key-here"

# Google OAuth settings
GOOGLE_CLIENT_ID = "your-client-id.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "GOCSPX-your-client-secret"
ALLOWED_EMAIL = "your.email@gmail.com"
```

## API Reference

### Add Download
```http
POST /{WEBHOOK_PATH}
```

| Parameter | Type | Description |
|----------|------|-------------|
| `url` | `url` | **Required**. URL to stream |
| `subtitle_lang` | `lang abbreviation` | Language (ie 'en'/'de'/'fr' etc) |

### Check Status
```http
GET /{STATUS_PATH}
```
Requires Google OAuth login (browser session). A visual dashboard is available at `/status-page`.

## Chrome Extension

Load `ChromeExtension/` as an unpacked extension (chrome://extensions → Developer mode → Load unpacked).

Configure in the popup:
- **Server URL**: the FULL webhook URL, e.g. `https://yourdomain.com/your-webhook-path` (not the video page URL!)
- **Token**: one of the values from `API_TOKENS` in `config.py`

Optional: copy `ChromeExtension/defaults.example.js` to `defaults.js` and fill in your values to prefill both fields automatically. `defaults.js` is gitignored so secrets never reach the repo.

## Deployment

### Docker Deployment
```bash
docker run -d --name mediamarauder --restart unless-stopped \
    -p 5000:5000 \
    -v /{path_to_download_mount}:/app/downloads \
    -v /{path_to_config}/config.py:/app/config.py \
    mathin/mediamarauder:latest
```

### Local Development Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/hindfelt/MediaMarauder.git
   cd MediaMarauder
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python app.py
   ```

## Security
- Google OAuth authentication with email restriction (fails closed if `ALLOWED_EMAIL` unset)
- Domain whitelist with strict dot-boundary matching (no suffix bypass)
- Constant-time API token comparison
- Validated subtitle language input before it reaches yt-dlp
- Secure session cookies (Secure, HttpOnly, SameSite=Lax) -- requires HTTPS for login
- HTTPS via Caddy or other TLS-terminating reverse proxy (required in production)
- `.dockerignore` prevents secrets from being baked into images
- Security test suite: `python test_security.py` (24 tests)

## Changelog

### 2026-07-19
**Security Hardening & Dependency Fixes**
- **Fixed:** Domain whitelist bypass -- `evilyoutube.com` no longer matches `youtube.com`; matching now uses `parsed.hostname` with exact or dot-boundary comparison
- **Fixed:** API token check now constant-time (`secrets.compare_digest`)
- **Fixed:** 500 responses no longer leak exception details; errors logged server-side
- **Fixed:** `subtitle_lang` validated (`[a-zA-Z]{2,3}`) before reaching yt-dlp argv
- **Fixed:** OAuth fails closed when `ALLOWED_EMAIL` is unset; email compare case-insensitive
- **Fixed:** Flask upgraded to >=3.1 (2.2.5 was incompatible with werkzeug >=3.1); Authlib 1.6.6; restored `requests` dependency
- **Fixed:** `DOWNLOAD_PATH` joined with `os.path.join` (no more trailing-slash requirement)
- **Added:** Secure/HttpOnly/SameSite session cookie flags
- **Added:** `.dockerignore` (config.py, .git, venv, downloads excluded from images)
- **Added:** `test_security.py` -- 24 tests covering URL validation, filename sanitization, queue handling
- **Extension:** removed unused `scripting`/`tabs` permissions; optional `defaults.js` prefill for server URL and token
- **Cleanup:** removed dead code, debug prints; status endpoint restricted to GET

### 2026-06-26
**Code Cleanup & Configuration Improvements**
- **Fixed:** Flask `secret_key` now persistent via `SECRET_KEY` in `config.py` (sessions survive container restarts)
- **Fixed:** `config_example.py` now includes all config fields (OAuth, `SECRET_KEY`)
- **Fixed:** Removed hardcoded `/app/downloads` path in `download.py`
- **Removed:** Dead code -- `validateurl()` in `app.py`, `SecurityUtils.download_file()`, `/process-queue` endpoint, incomplete `save_file_in_series_folder()`
- **Added:** Architecture documentation in `docs/architecture.md`

### 2026-01-05
**Critical Bug Fix: Download Blocking Issue**
- **Fixed:** Downloads stopping mid-process due to subprocess stderr buffer blocking
- **Solution:** Redirected stderr to stdout in yt-dlp subprocess (download.py:151)
- **Impact:** Downloads now complete successfully regardless of size (tested with 3.9GB files)
- **Testing:** Verified with YouTube and SVT Play downloads

**Security Updates**
- Updated `urllib3` to >=2.6.0 (fixes CVE-2025-66471, CVE-2025-66418)
- Updated `werkzeug` to >=3.1.4 (fixes CVE-2025-66221)
- All high and medium severity vulnerabilities resolved

**UI/UX Improvements**
- Added loader animation at `/` (0x4d.in loader integration)
- Automatic redirect to landing page after 3 seconds
- Added `/landing` route for simple landing page
- Added login link on landing page for easier access to status page
- Fixed HTML closing tag on Github link

**Code Improvements**
- Improved error handling to use process return codes
- Enabled graceful queue processor shutdown via `stop_processing_flag`
- Better error messages for failed downloads

**Technical Details:**
The subprocess blocking issue occurred when yt-dlp wrote warnings or errors to stderr. With stderr as a separate pipe, the buffer would fill and block indefinitely. By redirecting stderr to stdout (`stderr=subprocess.STDOUT`), all output flows through one stream that's actively consumed, preventing blocking.

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
This project is licensed under the MIT License - see the LICENSE file for details
