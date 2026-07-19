"""Unit tests for security-critical modules."""

import os
import sys
import unittest
from unittest.mock import patch

# Ensure project root is on sys.path so imports resolve
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestDownloaderSanitizeFilename(unittest.TestCase):
    """Test Downloader.sanitize_filename() - filename safety."""

    def setUp(self):
        from download import Downloader
        self.d = Downloader()

    def test_simple_filename(self):
        self.assertEqual(self.d.sanitize_filename("https://example.com/video.mp4"), "video.mp4")

    def test_encoded_filename(self):
        import urllib.parse
        encoded = f"https://example.com/{urllib.parse.quote('my video (1).mp4')}"
        self.assertEqual(self.d.sanitize_filename(encoded), "my video (1).mp4")

    def test_strips_dangerous_characters(self):
        result = self.d.sanitize_filename("https://example.com/f<>i|le?.mp4")
        for ch in '<>:"/\\|?*':
            self.assertNotIn(ch, result, f"Dangerous character '{ch}' survived sanitization")

    def test_deep_path_returns_last_segment(self):
        result = self.d.sanitize_filename("https://example.com/a/b/c/file.mp4")
        self.assertEqual(result, "file.mp4")

    def test_no_extension(self):
        result = self.d.sanitize_filename("https://example.com/video")
        self.assertEqual(result, "video")


class TestSecurityUtilsValidateUrl(unittest.TestCase):
    """Test SecurityUtils.validate_url() - URL trust boundary."""

    def setUp(self):
        self._patcher = patch('securityUtils.WHITELISTED_DOMAINS', ['youtube.com', 'example.com'])
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def test_valid_http_url(self):
        from securityUtils import SecurityUtils
        self.assertTrue(SecurityUtils.validate_url("http://www.youtube.com/watch?v=abc"))

    def test_valid_https_url(self):
        from securityUtils import SecurityUtils
        self.assertTrue(SecurityUtils.validate_url("https://youtube.com/watch?v=abc"))

    def test_subdomain_matches_parent(self):
        from securityUtils import SecurityUtils
        self.assertTrue(SecurityUtils.validate_url("https://www.youtube.com/watch?v=abc"))

    def test_another_subdomain_matches_parent(self):
        from securityUtils import SecurityUtils
        self.assertTrue(SecurityUtils.validate_url("https://m.youtube.com/watch?v=abc"))

    def test_rejects_domain_suffix_without_dot_boundary(self):
        from securityUtils import SecurityUtils
        with self.assertRaises(ValueError):
            SecurityUtils.validate_url("https://evilyoutube.com/watch?v=abc")

    def test_rejects_non_whitelisted_domain(self):
        from securityUtils import SecurityUtils
        with self.assertRaises(ValueError):
            SecurityUtils.validate_url("https://evil.com/malware")

    def test_rejects_non_http_scheme(self):
        from securityUtils import SecurityUtils
        with self.assertRaises(ValueError):
            SecurityUtils.validate_url("ftp://youtube.com/file")

    def test_rejects_missing_host(self):
        from securityUtils import SecurityUtils
        with self.assertRaises(ValueError):
            SecurityUtils.validate_url("https:///no-host")

    def test_rejects_semicolon_injection(self):
        from securityUtils import SecurityUtils
        with self.assertRaises(ValueError):
            SecurityUtils.validate_url("https://youtube.com/watch?v=abc;rm -rf /")

    def test_rejects_pipe_injection(self):
        from securityUtils import SecurityUtils
        with self.assertRaises(ValueError):
            SecurityUtils.validate_url("https://youtube.com/watch?v=abc|curl evil.com")

    def test_rejects_double_ampersand_injection(self):
        from securityUtils import SecurityUtils
        with self.assertRaises(ValueError):
            SecurityUtils.validate_url("https://youtube.com/watch?v=abc&&wget evil.com")

    def test_empty_url(self):
        from securityUtils import SecurityUtils
        with self.assertRaises(ValueError):
            SecurityUtils.validate_url("")


class TestSecurityUtilsSanitizeFilename(unittest.TestCase):
    """Test SecurityUtils.sanitize_filename() - path safety."""

    def test_normal_filename(self):
        from securityUtils import SecurityUtils
        self.assertEqual(SecurityUtils.sanitize_filename("video.mp4"), "video.mp4")

    def test_removes_dangerous_chars(self):
        from securityUtils import SecurityUtils
        result = SecurityUtils.sanitize_filename('f<>i:"le\\|?.mp4')
        self.assertEqual(result, "file.mp4")


class TestSecurityUtilsEnsureSafePath(unittest.TestCase):
    """Test SecurityUtils.ensure_safe_path() - directory traversal protection."""

    def test_safe_path(self):
        from securityUtils import SecurityUtils
        result = SecurityUtils.ensure_safe_path("/tmp/base", "file.mp4")
        self.assertTrue(result.startswith("/tmp/base"))

    def test_blocks_directory_traversal(self):
        from securityUtils import SecurityUtils
        # sanitize_filename strips '/' so "../../../etc/passwd" becomes "....etcpasswd"
        # The result is safe -- it stays inside base_folder
        result = SecurityUtils.ensure_safe_path("/tmp/base", "../../../etc/passwd")
        self.assertTrue(result.startswith("/tmp/base"))
        self.assertEqual(result, "/tmp/base/......etcpasswd")


class TestDownloaderQueue(unittest.TestCase):
    """Test Downloader queue thread safety basics."""

    def setUp(self):
        from download import Downloader
        self.d = Downloader()

    def test_add_and_get_queue(self):
        self.d.add_to_queue(("https://youtube.com/watch?v=abc", "en"))
        queue = self.d.get_queue()
        self.assertEqual(len(queue), 1)
        self.assertEqual(queue[0][0], "https://youtube.com/watch?v=abc")

    def test_empty_queue_initially(self):
        self.assertEqual(self.d.get_queue(), [])

    def test_processing_defaults_to_false(self):
        self.assertFalse(self.d.is_processing())


if __name__ == '__main__':
    unittest.main()
