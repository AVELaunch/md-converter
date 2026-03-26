#!/bin/bash
# launch.command -- Double-click in Finder to run MD Converter
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
"$PROJECT_DIR/.venv/bin/python3" "$PROJECT_DIR/src/converter_app.py"
