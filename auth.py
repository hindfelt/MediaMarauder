from functools import wraps
from flask import session, jsonify, redirect, url_for
from authlib.integrations.flask_client import OAuth
from authlib.integrations.base_client.errors import OAuthError
from config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, ALLOWED_EMAIL, SECRET_KEY


def init_auth(app):

    app.secret_key = SECRET_KEY
    app.config.update(
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
    )

    oauth = OAuth(app)
    google = oauth.register(
        name='google',
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'}
     )

    def login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user' not in session:
                return jsonify({"error": "Unauthorized"}), 401
            return f(*args, **kwargs)
        return decorated_function

    @app.route('/auth')
    def auth():
        try:
            token = google.authorize_access_token()
            userinfo = token.get('userinfo')
            if userinfo:
                allowed_email = (ALLOWED_EMAIL or '').strip()
                user_email = (userinfo.get('email') or '').strip()
                if not allowed_email or user_email.lower() != allowed_email.lower():
                    return 'Unauthorized email', 401
                session['user'] = userinfo
                return redirect('/status-page')
        except OAuthError as e:
            print(f"OAuth error: {str(e)}")
            return redirect('/login')
        except Exception as e:
            print(f"Authentication error: {str(e)}")
            return 'Authentication failed', 400

        return 'Failed to get user info', 400

    @app.route('/login')
    def login():
        redirect_uri = url_for('auth', _external=True)
        return google.authorize_redirect(redirect_uri)

    @app.route('/logout')
    def logout():
        session.pop('user', None)
        return redirect('/')

    return login_required
