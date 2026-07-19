import os
import re
from urllib.parse import urlparse, unquote
from config import WHITELISTED_DOMAINS


class SecurityUtils:
    @staticmethod
    def validate_url(url):
        parsed = urlparse(url)

        if parsed.scheme not in ("http", "https"):
            raise ValueError(f"Invalid URL scheme: {parsed.scheme}")

        host = parsed.hostname
        if not host:
            raise ValueError("Invalid URL: Missing host")

        host = host.lower()
        allowed_domains = (domain.lower() for domain in WHITELISTED_DOMAINS)
        if not any(host == domain or host.endswith('.' + domain) for domain in allowed_domains):
            raise ValueError(f"Domain not allowed: {host}")

        if any(char in url for char in [';', '|', '&&']):
            raise ValueError("Malicious characters detected in URL")

        return True

    @staticmethod
    def sanitize_filename(filename):
        sanitized = re.sub(r'[<>:"/\\|?*]', '', filename).strip()
        return sanitized

    @staticmethod
    def ensure_safe_path(base_folder, filename):
        sanitized_filename = SecurityUtils.sanitize_filename(filename)
        safe_path = os.path.join(os.path.abspath(base_folder), sanitized_filename)
        if not safe_path.startswith(os.path.abspath(base_folder)):
            raise ValueError(f"Unsafe file path: {safe_path}")
        return safe_path
