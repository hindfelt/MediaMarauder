from flask import Flask, request, jsonify
import threading
import time
from download import check_for_files, downloaded_files

app = Flask(__name__)
url_queue = []
downloaded_files = []

@app.route("/svtdl-hook", methods=["POST"])
def webhook():
    data = request.json
    url = data.get("url")
    if url:
        url_queue.append(url)
        return jsonify({"status": "URL added to the queue"}), 200
    return jsonify({"error": "Invalid data"}), 400

@app.route("/status", methods=["GET"])
def status():
    return jsonify({
        "queue": url_queue,
        "downloaded_files": downloaded_files
    })


def poll_urls():
    while True:
        if url_queue:
            url = url_queue.pop(0)
            print(f"Processing URL: {url}")
            # check_for_files(url)
        time.sleep(120)  # Poll every 2 minutes

# Start polling in a separate thread
threading.Thread(target=poll_urls, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)