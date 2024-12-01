import os
import re
from urllib.parse import urlparse, unquote
import requests
from config import WHITELISTED_DOMAINS


class SecurityUtils:
    @staticmethod
    def validate_url(url):
        """
        Validate the URL structure and ensure it belongs to an allowed domain.
        """
        parsed = urlparse(url)

        # Check URL scheme
        if not parsed.scheme.startswith("http"):
            raise ValueError(f"Invalid URL scheme: {parsed.scheme}")

        # Check netloc (host)
        if not parsed.netloc:
            raise ValueError("Invalid URL: Missing host")

        # Check if the domain is allowed
        if not any(parsed.netloc.endswith(domain) for domain in WHITELISTED_DOMAINS):
            raise ValueError(f"Domain not allowed: {parsed.netloc}")
        
        # Reject URLs with dangerous characters
        if any(char in url for char in [';', '|', '&&']):
            raise ValueError("Malicious characters detected in URL")


        return True

    @staticmethod
    def sanitize_filename(filename):
        """
        Sanitize filenames to remove invalid or dangerous characters.
        """
        sanitized = re.sub(r'[<>:"/\\|?*]', '', filename).strip()
        return sanitized

    @staticmethod
    def ensure_safe_path(base_folder, filename):
        """
        Ensure that the resolved file path is within the base folder to prevent directory traversal.
        """
        # Sanitize the filename
        sanitized_filename = SecurityUtils.sanitize_filename(filename)
        
        # Construct the absolute path
        safe_path = os.path.join(os.path.abspath(base_folder), sanitized_filename)

        # Ensure the path is within the base folder
        if not safe_path.startswith(os.path.abspath(base_folder)):
            raise ValueError(f"Unsafe file path: {safe_path}")

        return safe_path

    @staticmethod
    def download_file(url, save_path, timeout=10):
        """
        Download a file from a URL with a timeout and save it to the specified path.
        """
        try:
            # Validate the URL before downloading
            SecurityUtils.validate_url(url)

            # Perform the download
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()  # Raise exception for HTTP errors
            
            # Save the file
            with open(save_path, "wb") as f:
                f.write(response.content)

            print(f"File downloaded successfully: {save_path}")
            return True
        except Exception as e:
            print(f"Error downloading file: {e}")
            return False
