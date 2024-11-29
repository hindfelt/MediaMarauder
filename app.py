from flask import Flask, request, jsonify, render_template
from threading import Thread
from download import Downloader

app = Flask(__name__)
downloader = Downloader()

@app.route('/')
def home():
    """
    Serve the default homepage from a template file.
    """
    return render_template('index.html')

@app.route('/svtdl-hook', methods=['POST'])
def webhook():
    """
    Add a URL to the download queue.
    """
    data = request.json
    url = data.get('url')
    subtitle_lang = data.get('subtitle_lang')
    if url:
        downloader.add_to_queue((url, subtitle_lang or None))
        return jsonify({"status": "URL added to the queue with subtitles" if subtitle_lang else "URL added to the queue"}), 200
    return jsonify({"error": "Invalid data"}), 400


@app.route('/status', methods=['GET'])
def status():
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

   # app.run(host="0.0.0.0", port=5000, ssl_context=('/app/certs/fullchain.pem', '/app/certs/privkey.pem'))
