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
        """Mock requests.get — no network access."""
        fake_html = (
            "<html><head><title>Mock Page</title></head>"
            "<body><p>Hello from mock.</p></body></html>"
        )
        fake_resp = mock.MagicMock()
        fake_resp.text = fake_html
        fake_resp.raise_for_status = mock.MagicMock()

        with tempfile.TemporaryDirectory() as td:
            with mock.patch("converters.requests.get", return_value=fake_resp):
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


if __name__ == "__main__":
    unittest.main()
