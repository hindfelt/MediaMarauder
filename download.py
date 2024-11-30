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
        self.lock = threading.Lock()  # To ensure thread-safe queue handling

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

    def download_file(self, url, subtitle_lang=None):
        """
        Download a file using yt-dlp.
        """
        print("--------------------------------")
        print('Langugage: ', subtitle_lang)

         # Assume `filename` is extracted from the URL
        print(f"url: {url}")
        sanitized_filename = self.sanitize_filename(url) 
        print(f"sanitized_filename: {sanitized_filename}")
        sanitized_folder = self.save_file_in_series_folder(sanitized_filename)
        print(f"sanitized_folder: {sanitized_folder}")
        # Save the file with the sanitized name
        filepath = os.path.join("/app/downloads", sanitized_filename)
        
        try:
            yt_dlp_command = [
                "yt-dlp",
                "-S", "codec:h264",
                # "-o", f"{DOWNLOAD_PATH}/{sanitized_filename}.%(ext)s", 
                "-o", f"{DOWNLOAD_PATH}/{sanitized_folder}%(title)s.%(ext)s", 
                "--format", "bestvideo*+bestaudio[language!=?sv-x-tal]", # Save to configured path
                "--yes-playlist", url
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
            print("--------------------------------")
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
