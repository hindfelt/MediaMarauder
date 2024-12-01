from flask import Flask, request, jsonify, render_template
from threading import Thread
from download import Downloader
from securityUtils import SecurityUtils
from config import API_TOKENS
from config import WEBHOOK_PATH
from config import STATUS_PATH


app = Flask(__name__)
downloader = Downloader()

@app.route('/')
def home():
    """
    Serve the default homepage from a template file!
    """
    return render_template('index.html')

@app.route(WEBHOOK_PATH, methods=['POST'])
def webhook():
    token = request.headers.get("Auth")
    if not token or token not in API_TOKENS.values():
        return jsonify({"Error": "Unauthorized"}), 401
    
    try: 
        """
        Add a URL to the download queue.
        """
        data = request.json
        url = data.get('url')
        subtitle_lang = data.get('subtitle_lang')
        
        if not url:
            return jsonify({"Error": "Missing URL"}), 400
        
        # sec validation
        SecurityUtils.validate_url(url)
        
        downloader.add_to_queue((url, subtitle_lang or None))
        return jsonify({"status": "URL added to the queue with subtitles" if subtitle_lang else "URL added to the queue"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Internl Server Error", "details": str(e)}), 500

def validateurl(url):
    try:
        print("----- validating security ---")
        SecurityUtils.validate_url(url)  # validation logic
        return True
    except ValueError as e:
        print(f"Security validation failed for URL: {e}")
        return False

@app.route(STATUS_PATH, methods=['POST'])
def status():
    token = request.headers.get("Auth")
    if not token or token not in API_TOKENS.values():
        return jsonify({"Error": "Unauthorized"}), 401
    """
    Return the current download queue and completed downloads.
    """
    return jsonify({
        "queue": downloader.get_queue(),
        "downloaded_files": downloader.get_downloaded_files()
    })


@app.route('/process-queue', methods=['POST'])
def process_queue():
    """
    Start processing the queue in a separate thread.
    """
    if not downloader.is_processing():
        thread = Thread(target=downloader.process_queue)
        thread.daemon = True
        thread.start()
        return jsonify({"status": "Processing started"}), 200
    return jsonify({"status": "Already processing"}), 200


def start_queue_processor():
    """
    Automatically start the queue processor in a background thread.
    And dance a little
    """
    thread = Thread(target=downloader.process_queue)
    thread.daemon = True  # Ensure the thread exits when the app stops
    thread.start()


if __name__ == "__main__":
    start_queue_processor()  # Start queue processor automaticall
    app.run(host="0.0.0.0", port=5000)  # No ssl_context
