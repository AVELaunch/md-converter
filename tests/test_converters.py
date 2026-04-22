"""Round-trip tests for each converter in src/converters.py."""

import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

# Ensure src/ is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import converters

FIXTURES = Path(__file__).resolve().parent / "fixtures"


class TestConvertTxt(unittest.TestCase):
    def test_round_trip(self):
        with tempfile.TemporaryDirectory() as td:
            r = converters.convert_txt(str(FIXTURES / "sample.txt"), Path(td))
            self.assertTrue(r.success)
            self.assertTrue(Path(r.output_path).exists())
            self.assertGreater(r.word_count, 0)
            content = Path(r.output_path).read_text()
            self.assertIn("# ", content)


class TestConvertHtml(unittest.TestCase):
    def test_round_trip_file(self):
        with tempfile.TemporaryDirectory() as td:
            r = converters.convert_html(str(FIXTURES / "sample.html"), Path(td))
            self.assertTrue(r.success)
            self.assertTrue(Path(r.output_path).exists())
            self.assertGreater(r.word_count, 0)
            content = Path(r.output_path).read_text()
            self.assertIn("# ", content)

    def test_round_trip_url(self):
        """Mock _safe_get — no network access."""
        fake_html = (
            "<html><head><title>Mock Page</title></head>"
            "<body><p>Hello from mock.</p></body></html>"
        )
        fake_result = converters.FetchResult(
            content=fake_html.encode("utf-8"),
            encoding="utf-8",
        )

        with tempfile.TemporaryDirectory() as td:
            with mock.patch("converters._safe_get", return_value=fake_result):
                r = converters.convert_html("https://example.com/test", Path(td))
            self.assertTrue(r.success)
            self.assertTrue(Path(r.output_path).exists())
            self.assertGreater(r.word_count, 0)


class TestConvertDocx(unittest.TestCase):
    def test_round_trip(self):
        with tempfile.TemporaryDirectory() as td:
            r = converters.convert_docx(str(FIXTURES / "sample.docx"), Path(td))
            self.assertTrue(r.success)
            self.assertTrue(Path(r.output_path).exists())
            self.assertGreater(r.word_count, 0)
            content = Path(r.output_path).read_text()
            self.assertIn("# ", content)


class TestConvertPdf(unittest.TestCase):
    def test_round_trip(self):
        with tempfile.TemporaryDirectory() as td:
            r = converters.convert_pdf(str(FIXTURES / "sample.pdf"), Path(td))
            self.assertTrue(r.success)
            self.assertTrue(Path(r.output_path).exists())
            self.assertGreater(r.word_count, 0)
            content = Path(r.output_path).read_text()
            self.assertIn("# ", content)


class TestConvertPdfOcr(unittest.TestCase):
    @unittest.skipUnless(shutil.which("tesseract"), "tesseract not installed")
    def test_round_trip_scanned(self):
        with tempfile.TemporaryDirectory() as td:
            r = converters.convert_pdf(str(FIXTURES / "sample_scanned.pdf"), Path(td))
            self.assertTrue(r.success)
            self.assertTrue(Path(r.output_path).exists())
            self.assertGreater(r.word_count, 0)
            content = Path(r.output_path).read_text()
            self.assertIn("# ", content)


class TestConvertRtf(unittest.TestCase):
    def test_round_trip(self):
        with tempfile.TemporaryDirectory() as td:
            r = converters.convert_rtf(str(FIXTURES / "sample.rtf"), Path(td))
            self.assertTrue(r.success)
            self.assertTrue(Path(r.output_path).exists())
            self.assertGreater(r.word_count, 0)
            content = Path(r.output_path).read_text()
            self.assertIn("# ", content)


class TestSafeGet(unittest.TestCase):
    def test_rejects_file_scheme(self):
        with self.assertRaises(ValueError):
            converters._safe_get("file:///etc/passwd")

    def test_rejects_loopback(self):
        with self.assertRaises(ValueError):
            converters._safe_get("http://127.0.0.1/")

    def test_rejects_metadata(self):
        with self.assertRaises(ValueError):
            converters._safe_get("http://169.254.169.254/")

    def test_size_cap(self):
        """Responses exceeding the size cap raise ValueError."""
        fake_resp = mock.MagicMock()
        fake_resp.raise_for_status = mock.MagicMock()
        fake_resp.history = []
        # Return chunks that exceed a small cap
        fake_resp.iter_content = mock.MagicMock(return_value=[b"x" * 2048])

        with mock.patch("converters.requests.get", return_value=fake_resp):
            with mock.patch("converters._is_private_ip", return_value=False):
                with mock.patch.object(converters, "_MAX_RESPONSE_BYTES", 1024):
                    with self.assertRaises(ValueError) as ctx:
                        converters._safe_get("https://example.com/big")
                    self.assertIn("limit", str(ctx.exception).lower())


if __name__ == "__main__":
    unittest.main()
