import subprocess
import time
import threading
from config import DOWNLOAD_PATH


class Downloader:
    def __init__(self):
        self.url_queue = []
        self.downloaded_files = []
        self.processing = False
        self.stop_processing_flag = False  # Initialize stop flag
        self.lock = threading.Lock()  # To ensure thread-safe queue handling

    def add_to_queue(self, item):
        """
        Add a URL to the download queue.
        """
        with self.lock:
            self.url_queue.append(item)

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

    def download_file(self, url, subtitle_lang=None):
        """
        Download a file using yt-dlp.
        """
        print('Lnagugage: ', subtitle_lang)
        try:
            yt_dlp_command = [
                "yt-dlp",
                "-S", "codec:h264",
                "-o", f"{DOWNLOAD_PATH}/%(title)s.%(ext)s", 
                "--format", "bestvideo*+bestaudio[language!=?sv-x-tal]", # Save to configured path
                url
            ]
            
            if subtitle_lang:
                yt_dlp_command.extend(["--convert-subs", "srt","--write-subs", "--sub-lang", subtitle_lang])
            
            print(yt_dlp_command)

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
                self.downloaded_files.append({"url": url, "status": "Downloaded", "sub": subtitle_lang if subtitle_lang else "none" })
            return True

        except subprocess.CalledProcessError as e:
            print(f"Error running yt-dlp: {e.stderr}")
            with self.lock:
                self.downloaded_files.append({"url": url, "status": f"Error: {e.stderr}"})
            return False
    
    def stop_processing(self):
        """
        Signal the queue processor to stop.
        """
        self.stop_processing_flag = True
    
    def process_queue(self):
        """
        Continuously check the queue and process downloads when there are URLs.
        """
        self.processing = True
        print("Queue processor started.")

        while True:
            with self.lock:
                if self.url_queue:
                    item = self.url_queue.pop(0)
                    print(f"Queue contents: {self.url_queue}")
                    url, subtitle_lang = item  # Extract URL and subtitle language
                else:
                    item = None

            if item:
                print(f"Processing URL: {url} with subtitles: {subtitle_lang}")
                self.download_file(url, subtitle_lang + '.*' if subtitle_lang else None)
                time.sleep(1)  # Add a small delay to avoid rapid processing
            else:
                # If the queue is empty, wait before checking again
                time.sleep(5)

        self.processing = False
        print("Queue processor stopped.")
