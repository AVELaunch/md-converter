# MD Converter

Convert PDF, DOCX, HTML, TXT, and RTF files to clean Markdown.
Drag-and-drop GUI or command line. Runs 100% locally -- no API calls, no cloud.

Scanned PDFs are handled automatically via Tesseract OCR.

## Quick Start (macOS)

```bash
# 1. Clone
git clone https://github.com/Gadamad/md-converter.git
cd md-converter

# 2. Install (creates venv, installs deps, builds .app, copies to /Applications)
bash install.sh

# 3. Open from Launchpad, Spotlight, or Finder > Applications
```

## Requirements

- macOS (GUI uses native WebKit via pywebview)
- Python 3.10+
- Tesseract OCR (optional, for scanned PDFs): `brew install tesseract`

## Command Line Usage

```bash
# Convert specific files
.venv/bin/python3 src/converter_app.py document.pdf report.docx page.html

# Convert a URL
.venv/bin/python3 src/converter_app.py https://example.com/article
```

Output goes to `converted/` organized by file type (pdf/, docx/, html/, txt/, rtf/).

## Obsidian Vault Delivery (Optional)

To auto-copy converted files to your Obsidian vault:

```bash
cp config.example.json config.json
# Edit config.json and set your vault path
```

## Build Standalone App

```bash
# Requires pyinstaller: pip install pyinstaller
bash scripts/build_app.sh
# Creates: src/dist/MD Converter.app
```

## Supported Formats

| Format | Features |
|--------|----------|
| PDF | Text extraction + OCR fallback for scanned pages |
| DOCX | Headings, bold/italic, lists, tables preserved |
| HTML | Fetches URLs or reads local files, strips nav/scripts |
| TXT | Wraps in metadata header |
| RTF | Strips RTF formatting to plain Markdown |

## Project Structure

```
md-converter/
  src/
    converter_app.py   # GUI app (pywebview)
    converters.py      # All format converters
    native_drop.py     # macOS native drag-and-drop
  scripts/
    install.sh         # Setup script
    launch.command     # Double-click launcher
    build_app.sh       # PyInstaller build
  converted/           # Output (created on first run)
  config.json          # Your vault path (optional, git-ignored)
  config.example.json  # Template
  requirements.txt     # Python dependencies
```
