DOWNLOAD_PATH = "path/to/downloads"
WEBHOOK_PATH = "/{server-path-for-webhook ie /webhook}"
STATUS_PATH = "/{server-path-for-status-call ie /status}"
WHITELISTED_DOMAINS = [
    "url.com",
    "youtube.com"
]
API_TOKENS = {
    "user": "password",
    "user2": "password"
}

# Flask session secret key -- generate with: python -c "import os; print(os.urandom(24).hex())"
SECRET_KEY = "your-secret-key-here"

# Google OAuth settings
GOOGLE_CLIENT_ID = "your-client-id.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "GOCSPX-your-client-secret"
ALLOWED_EMAIL = "your.email@gmail.com"
