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
        self.stop_processing_flag = False  # Initialize stop flag
        self.current_download_status = "Idle"
        self.current_download_percentage = 0

    def get_current_download_percentage(self):
        """
        Return the current download percentage.
        """
        with self.lock:
            return self.current_download_percentage

    def get_current_download_status(self):
        """
        Return the current download status.
        """
        with self.lock:
            return self.current_download_status

    def sanitize_filename(self,url):
        """
        Extract a meaningful filename from the URL.
        """
        # Parse the URL
        parsed_url = urlparse(url)
        print("--------------------------------")
        # Get the path part of the URL and split it into components
        path_parts = parsed_url.path.split('/')
        print(f"path: ' {path_parts}")

        # Assume the meaningful part is the last segment in the path
        raw_filename = path_parts[-1]
        print(f"raw filename: ' {raw_filename}")

        # Decode URL-encoded parts (e.g., %20 -> space)
        decoded_filename = unquote(raw_filename)
        print(f"decoded filename: ' {decoded_filename}")

        # Remove unwanted characters (e.g., square brackets, special chars)
        sanitized_filename = re.sub(r'[<>:"/\\|?*]', '', decoded_filename).strip()
        print("sanitized filedname: ", sanitized_filename)
        print("--------------------------------")
        return sanitized_filename
 
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

    def save_file_in_series_folder(self, sanitized_filename):
        """
        Creates series folder and saves the episode file within it.
        """
        base_folder = "./"
        
        print("--------------------------------")
        # Extract series and episode namesç
        #series_name, episode_title = extract_series_and_filename(url)
        print(f"sanitized_filename in save_file_in_series_folder: {sanitized_filename}")
        # Create a folder for the series
        series_folder = os.path.join(base_folder, sanitized_filename)
        print(f"series_folder in save_file_in_series_folder: {series_folder}")
    
        print(f"Base folder writable: {os.access(base_folder, os.W_OK)}")
        print(f"Series folder path: {series_folder}")
        print(f"Is series folder writable: {os.access(os.path.dirname(series_folder), os.W_OK)}")
        #os.makedirs(series_folder, exist_ok=True)

        # Full path to the file
        file_path = os.path.join(series_folder, sanitized_filename)
        print(f"file_path in save_file_in_series_folder: {file_path}")
        print("--------------------------------")
    
        return file_path

    def download_file(self, url, subtitle_lang=None):\n        \"\"\"\n        Download a file using yt-dlp.\n        \"\"\"\n        with self.lock:\n            self.current_download_status = f\"Starting download for {url}\"\n            self.current_download_percentage = 0\n\n        print(\"--------------------------------\")\n        print('Langugage: ', subtitle_lang)\n\n         # Assume `filename` is extracted from the URL\n        print(f\"url: {url}\")\n        sanitized_filename = self.sanitize_filename(url) \n        print(f\"sanitized_filename: {sanitized_filename}\")\n        sanitized_folder = self.save_file_in_series_folder(sanitized_filename)\n        print(f\"sanitized_folder: {sanitized_folder}\")\n        # Save the file with the sanitized name\n        filepath = os.path.join(\"/app/downloads\", sanitized_filename)\n        \n        try:\n            with self.lock:\n                self.current_download_status = f\"Downloading {url}...\"\n            yt_dlp_command = [\n                \"yt-dlp\",\n                \"--progress\",\n                \"-o\", f\"{DOWNLOAD_PATH}/{sanitized_folder}%(title)s.%(ext)s\",\n                \"--recode-video\", \"mp4\",\n                \"--yes-playlist\", url,\n            ]\n            \n            if subtitle_lang:\n                yt_dlp_command.extend([\"--write-subs\", \"--sub-lang\", subtitle_lang, \"--convert-subs\", \"srt\"])\n            \n            print(yt_dlp_command)\n\n            process = subprocess.Popen(\n                yt_dlp_command,\n                stdout=subprocess.PIPE,\n                stderr=subprocess.PIPE,\n                text=True,\n                bufsize=1,\n                universal_newlines=True\n            )\n\n            for line in process.stdout:\n                print(line, end='')\n                match = re.search(r\"\[download\]\\s+([0-9.]+)%\", line)\n                if match:\n                    with self.lock:\n                        self.current_download_percentage = float(match.group(1))\n\n            process.wait()\n\n            if process.returncode == 0:\n                with self.lock:\n                    self.downloaded_files.append({\"url\": url, \"status\": \"Downloaded\", \"sub\": subtitle_lang if subtitle_lang else \"none\" })\n                    self.current_download_status = f\"Download completed for {url}\"\n                    self.current_download_percentage = 100\n                return True\n            else:\n                error_output = process.stderr.read()\n                print(f\"Error running yt-dlp: {error_output}\")\n                with self.lock:\n                    self.downloaded_files.append({\"url\": url, \"status\": f\"Error: {error_output}\"})\n                    self.current_download_status = f\"Error downloading {url}: {error_output}\"\n                    self.current_download_percentage = 0\n                return False\n\n        except Exception as e:\n            print(f\"An unexpected error occurred: {e}\")\n            with self.lock:\n                self.downloaded_files.append({\"url\": url, \"status\": f\"Error: {e}\"})\n                self.current_download_status = f\"Error downloading {url}: {e}\"\n                self.current_download_percentage = 0\n            return False
    
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
        with self.lock:
            self.current_download_status = "Starting queue processor..."

        while True:
            with self.lock:
                if self.url_queue:
                    item = self.url_queue.pop(0)
                    print(f"Queue contents: {self.url_queue}")
                    url, subtitle_lang = item  # Extract URL and subtitle language
                    self.current_download_status = f"Processing {url} with subtitles: {subtitle_lang}"
                else:
                    item = None
                    self.current_download_status = "Waiting for new URLs..."

            if item:
                print(f"Processing URL: {url} with subtitles: {subtitle_lang}")
                self.download_file(url, subtitle_lang + '.*' if subtitle_lang else None)
                time.sleep(1)  # Add a small delay to avoid rapid processing
            else:
                # If the queue is empty, wait before checking again
                time.sleep(5)

        self.processing = False
        with self.lock:
            self.current_download_status = "Idle"
        print("Queue processor stopped.")
