# Changelog

Fork-specific changes. This fork originated from https://github.com/Gadamad/md-converter.

## [Unreleased]

### Added
- Marker as primary local OCR engine for scanned PDFs, with Tesseract as fallback.
- `ocr_engine` config option and `MD_CONVERTER_OCR` environment variable to control OCR engine selection (`auto`, `marker`, `tesseract`).
- SSRF protection on URL fetch: blocks private/reserved IPs, validates redirect hops, rejects non-HTTP schemes.
- 50 MB response size cap on URL fetch.
- `user_data_dir()` for writable output and config paths when running as a frozen `.app` bundle.
- Comprehensive test suite with fixtures for all supported formats and round-trip converter tests.
- YAML frontmatter escaping to prevent injection via titles containing quotes, backslashes, or newlines.
- Structured logging via `logging` module across converter app and native drop handler.
- Optional Marker model prefetch in `install.sh` via `MD_CONVERTER_PREFETCH=1`.
- PyYAML added to dependencies (used for frontmatter validation in tests).

### Changed
- URL fetching now uses `_safe_get()` with streaming, size limits, and SSRF guards instead of raw `requests.get()`.
- SSL `SSL_CERT_FILE` environment variable is now set only during URL fetch, not at module import time.
- Bare `except: pass` blocks replaced with specific exception types and logger warnings/errors.
- `print()` diagnostics in `native_drop.py` replaced with `logging`.

### Fixed
- YAML frontmatter values with special characters are now properly escaped via `json.dumps()`.
- Frozen app builds now write outputs and config to `~/Library/Application Support/MD Converter/` instead of the read-only app bundle directory.

### Security
- URL fetch blocks SSRF to private IPs (127.0.0.1, 169.254.x, 10.x, 192.168.x, 172.16-31.x), including via redirects.
- Rejects `file://` and other non-HTTP URL schemes.
- Removed `pdf_to_md.py` which contained a dangerous `os.system("pip install ...")` on ImportError.

### Removed
- Legacy root-level scripts: `pdf_to_md.py`, `pdf_ocr_to_md.py`, `docx_to_md.py` (superseded by `src/converters.py`).

### Known Issues
- Frozen `.app` builds produced by `build_app.sh` do not currently bundle
  Marker OCR dependencies, certifi CA bundle, or torch data files.
  Scanned-PDF conversion in frozen builds will fall back to Tesseract.
  To be resolved before the first tagged release — see build script TODO.
