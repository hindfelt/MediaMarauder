from functools import wraps
from flask import session, jsonify, redirect, url_for
from authlib.integrations.flask_client import OAuth
import os
from dotenv import load_dotenv
from authlib.integrations.base_client.errors import OAuthError

load_dotenv()

def init_auth(app):

    app.secret_key = os.urandom(24)
    
    oauth = OAuth(app)
    google = oauth.register(
        name='google',
        client_id=os.getenv('GOOGLE_CLIENT_ID'),
        client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
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
                allowed_email = os.getenv('ALLOWED_EMAIL')
                if allowed_email and userinfo['email'] != allowed_email:
                    return 'Unauthorized email', 401
                session['user'] = userinfo
                return redirect('/status-page')
        except OAuthError as e:
            # Handle OAuth errors (like access denied)
            print(f"OAuth error: {str(e)}")
            return redirect('/login')  # Redirect back to login
        except Exception as e:
            # Handle other errors
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

