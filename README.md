# MediaMarauder

A Dockerized video downloader system for offline viewing that processes URLs submitted via a Chrome extension. It downloads videos from supported platforms (using yt-dlp) with options for subtitles, using a Flask-based backend. The system features queue management, authentication (both token-based and Google OAuth), and organized storage.

## Features
- Secure Google OAuth authentication
- Token-based API authentication
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
5. Create OAuth 2.0 Client ID credentials
6. Add authorized redirect URIs:
   - `http://localhost:5000/google-auth`
   - `http://127.0.0.1:5000/google-auth`
7. Save your Client ID and Client Secret

### 2. Configuration Files

#### Environment Variables
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Fill in your `.env` file:
   ```
   GOOGLE_CLIENT_ID=your_client_id_here
   GOOGLE_CLIENT_SECRET=your_client_secret_here
   ALLOWED_EMAIL=your.email@gmail.com
   ```

#### Config.py Setup
Create `config.py` (stored outside container):
```python
DOWNLOAD_PATH = "path"
WEBHOOK_PATH = "/{webhook-name for adding urls}"
STATUS_PATH = "/{status-hook name}"
WHITELISTED_DOMAINS = [
    "video-service.domain",
    "another-video-service.domain"
]
API_TOKENS = {
    "user": "token"
}
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
- `.env` file excluded from git (via .gitignore)
- Google OAuth authentication
- API token validation for webhooks
- URL validation and security checks
- HTTPS support via Caddy (recommended)
- Whitelisted domains configuration

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
This project is licensed under the MIT License - see the LICENSE file for details