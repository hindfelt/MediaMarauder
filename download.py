import subprocess
import os
import re
import time
import threading
from config import DOWNLOAD_PATH
from urllib.parse import urlparse, unquote


class Downloader:
    def __init__(self):
        self.url_queue = []
        self.downloaded_files = []
        self.processing = False
        self.stop_processing_flag = False
        self.current_download_status = "Idle"
        self.current_download_percentage = 0
        self.lock = threading.Lock()

    def get_current_download_percentage(self):
        with self.lock:
            return self.current_download_percentage

    def get_current_download_status(self):
        with self.lock:
            return self.current_download_status

    def sanitize_filename(self, url):
        parsed_url = urlparse(url)
        path_parts = parsed_url.path.split('/')
        raw_filename = path_parts[-1]
        decoded_filename = unquote(raw_filename)
        sanitized_filename = re.sub(r'[<>:"/\\|?*]', '', decoded_filename).strip()
        return sanitized_filename

    def add_to_queue(self, item):
        with self.lock:
            self.url_queue.append(item)

    def get_queue(self):
        with self.lock:
            return self.url_queue.copy()

    def get_downloaded_files(self):
        with self.lock:
            return self.downloaded_files.copy()

    def is_processing(self):
        with self.lock:
            return self.processing

    def download_file(self, url, subtitle_lang=None):
        with self.lock:
            self.current_download_status = f"Starting download for {url}"
            self.current_download_percentage = 0

        print(f"url: {url}")

        try:
            with self.lock:
                self.current_download_status = f"Downloading {url}..."
            yt_dlp_command = [
                 "yt-dlp",
                 "--progress",
                 "-o", os.path.join(DOWNLOAD_PATH, "%(title)s.%(ext)s"),
                 "--recode-video", "mp4",
                 "--yes-playlist", url,
             ]

            if subtitle_lang:
                yt_dlp_command.extend(["--write-subs", "--sub-lang", subtitle_lang, "--convert-subs", "srt"])

            print(yt_dlp_command)

            process = subprocess.Popen(
                yt_dlp_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
             )

            for line in process.stdout:
                print(line, end='')
                match = re.search(r"\[download\]\s+([0-9.]+)%", line)
                if match:
                    with self.lock:
                        self.current_download_percentage = float(match.group(1))

            process.wait()

            if process.returncode == 0:
                with self.lock:
                    self.downloaded_files.append({"url": url, "status": "Downloaded", "sub": subtitle_lang if subtitle_lang else "none"})
                    self.current_download_status = f"Download completed for {url}"
                    self.current_download_percentage = 100
                return True
            else:
                error_msg = f"yt-dlp exited with code {process.returncode}"
                print(f"Error running yt-dlp: {error_msg}")
                with self.lock:
                    self.downloaded_files.append({"url": url, "status": f"Error: {error_msg}"})
                    self.current_download_status = f"Error downloading {url}: {error_msg}"
                    self.current_download_percentage = 0
                return False

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            with self.lock:
                self.downloaded_files.append({"url": url, "status": f"Error: {e}"})
                self.current_download_status = f"Error downloading {url}: {e}"
                self.current_download_percentage = 0
            return False

    def stop_processing(self):
        self.stop_processing_flag = True

    def process_queue(self):
        self.processing = True
        print("Queue processor started.")
        with self.lock:
            self.current_download_status = "Starting queue processor..."

        while not self.stop_processing_flag:
            with self.lock:
                if self.url_queue:
                    item = self.url_queue.pop(0)
                    print(f"Queue contents: {self.url_queue}")
                    url, subtitle_lang = item
                    self.current_download_status = f"Processing {url} with subtitles: {subtitle_lang}"
                else:
                    item = None
                    self.current_download_status = "Waiting for new URLs..."

            if item:
                print(f"Processing URL: {url} with subtitles: {subtitle_lang}")
                self.download_file(url, subtitle_lang + '.*' if subtitle_lang else None)
                with self.lock:
                    self.current_download_percentage = 0
                time.sleep(1)
            else:
                time.sleep(5)

        self.processing = False
        with self.lock:
            self.current_download_status = "Idle"
        print("Queue processor stopped.")
