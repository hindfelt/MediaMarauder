import subprocess
import time
import threading
from config import DOWNLOAD_PATH


class Downloader:
    def __init__(self):
        self.url_queue = []
        self.downloaded_files = []
        self.processing = False
        self.lock = threading.Lock()  # To ensure thread-safe queue handling

    def add_to_queue(self, url):
        """
        Add a URL to the download queue.
        """
        with self.lock:
            self.url_queue.append(url)

    def get_queue(self):
        """
        Return the current queue.
        """
        with self.lock:
            return self.url_queue.copy()

    def get_downloaded_files(self):
        """
        Return the list of downloaded files.
        """
        with self.lock:
            return self.downloaded_files.copy()

    def is_processing(self):
        """
        Check if processing is currently active.
        """
        return self.processing

    def download_file(self, url):
        """
        Download a file using yt-dlp.
        """
        try:
            yt_dlp_command = [
                "yt-dlp",
                "-f", "bv*[ext=mp4][vcodec^=avc1]+ba[ext=m4a]/b[ext=mp4]",
                "-S", "codec:h264",
                "-o", f"{DOWNLOAD_PATH}/%(title)s.%(ext)s",  # Save to configured path
                url
            ]

            # Run yt-dlp command
            result = subprocess.run(
                yt_dlp_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )

            print(f"yt-dlp output:\n{result.stdout}")
            with self.lock:
                self.downloaded_files.append({"url": url, "status": "Downloaded"})
            return True

        except subprocess.CalledProcessError as e:
            print(f"Error running yt-dlp: {e.stderr}")
            with self.lock:
                self.downloaded_files.append({"url": url, "status": f"Error: {e.stderr}"})
            return False

def process_queue(self):
        """
        Continuously check the queue and process downloads when there are URLs.
        """
        self.processing = True
        print("Queue processor started.")

        while True:
            with self.lock:
                if self.url_queue:
                    url = self.url_queue.pop(0)
                else:
                    url = None

            if url:
                print(f"Processing URL: {url}")
                self.download_file(url)
                time.sleep(1)  # Add a small delay to avoid rapid processing
            else:
                # If the queue is empty, wait before checking again
                time.sleep(5)

        # This line will never be reached because the loop runs indefinitely
        self.processing = False
