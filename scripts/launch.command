#!/bin/bash
# Launcher for MD Converter — opens the webview app from the venv.
# Double-click from Finder or run from Spotlight.
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR" || exit 1
source .venv/bin/activate
exec python src/converter_app.py
