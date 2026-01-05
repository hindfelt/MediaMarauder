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
DOWNLOAD_PATH = "downloads"
WEBHOOK_PATH = "/your-webhook-path"
STATUS_PATH = "/your-status-path"
WHITELISTED_DOMAINS = [
    "video-service.domain",
    "another-video-service.domain"
]
API_TOKENS = {
    "user": "your-api-token"
}

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
POST /{STATUS_PATH}
```

## Deployment

### Docker Deployment
```bash
docker run -d --name mediamarauder --restart unless-stopped \
    -p 5000:5000 \
    -v /{path_to_download_mount}:/app/downloads \
    -v /{path_to_config}/config.py:/app/config.py \
    --name mediamarauder mathin/mediamarauder:latest
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
- Google OAuth authentication with email restriction
- URL validation and security checks
- HTTPS support via Caddy (recommended)
- Whitelisted domains configuration
- Secure configuration management

## Changelog

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
