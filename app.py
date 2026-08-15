import mimetypes
import re
import secrets

from flask import Flask, request, jsonify, render_template
from threading import Thread
from auth import init_auth
from download import Downloader
from securityUtils import SecurityUtils
from config import API_TOKENS
from config import WEBHOOK_PATH
from config import STATUS_PATH


mimetypes.add_type("image/webp", ".webp")

app = Flask(__name__)
downloader = Downloader()
login_required = init_auth(app)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/landing')
def landing():
    return render_template('index2.html')


@app.route('/work/zieapp')
def zieapp_case_study():
    return render_template('zieapp.html')


@app.route(WEBHOOK_PATH, methods=['POST'])
def webhook():
    token = request.headers.get("Auth")
    valid_token = False
    if token:
        for configured_token in API_TOKENS.values():
            valid_token |= secrets.compare_digest(token, configured_token)
    if not valid_token:
        return jsonify({"Error": "Unauthorized"}), 401

    try:
        data = request.json
        url = data.get('url')
        subtitle_lang = data.get('subtitle_lang')

        if not url:
            return jsonify({"Error": "Missing URL"}), 400

        if subtitle_lang is not None and (
            not isinstance(subtitle_lang, str)
            or re.fullmatch(r'[a-zA-Z]{2,3}', subtitle_lang) is None
        ):
            return jsonify({"Error": "Invalid subtitle language"}), 400

        SecurityUtils.validate_url(url)

        downloader.add_to_queue((url, subtitle_lang or None))
        return jsonify({"status": "URL added to the queue with subtitles" if subtitle_lang else "URL added to the queue"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception:
        app.logger.exception("Unhandled error while processing webhook request")
        return jsonify({"error": "Internal Server Error"}), 500


@app.route(STATUS_PATH, methods=['GET'])
@login_required
def status():
    return jsonify({
         "queue": downloader.get_queue(),
         "downloaded_files": downloader.get_downloaded_files(),
         "current_status": downloader.get_current_download_status(),
         "current_download_percentage": downloader.get_current_download_percentage()
     })


@app.route('/status-page')
@login_required
def status_page():
    return render_template('status.html', STATUS_PATH=STATUS_PATH)


def start_queue_processor():
    thread = Thread(target=downloader.process_queue)
    thread.daemon = True
    thread.start()


if __name__ == "__main__":
    start_queue_processor()
    app.run(host="0.0.0.0", port=5000)
