#!/bin/bash
# Launcher for MD Converter — opens the webview app from the venv.
# Double-click from Finder or run from Spotlight.
cd "/Users/AVELaunch/Code/md-converter" || exit 1
source .venv/bin/activate
exec python src/converter_app.py
