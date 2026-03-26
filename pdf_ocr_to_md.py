#!/usr/bin/env python3
"""
PDF OCR to Markdown Converter
For scanned/image-based PDFs that have no selectable text.
Uses Tesseract OCR locally — no API calls, no tokens, no cost.
"""

import re
import sys
import time
from pathlib import Path

import fitz  # PyMuPDF — renders pages to images
import pytesseract
from PIL import Image


def ocr_pdf(pdf_path: str, dpi: int = 300) -> tuple[list[tuple[int, str]], int, int]:
    """
    Render each PDF page as an image and OCR it.
    Returns (pages, word_count, page_count).
    """
    doc = fitz.open(pdf_path)
    page_count = len(doc)
    pages = []
    total_words = 0
    zoom = dpi / 72  # 72 is default PDF DPI
    matrix = fitz.Matrix(zoom, zoom)

    for page_num in range(page_count):
        page = doc[page_num]
        pix = page.get_pixmap(matrix=matrix)

        # Convert pixmap to PIL Image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # Run Tesseract OCR
        text = pytesseract.image_to_string(img)

        if text.strip():
            pages.append((page_num + 1, text))
            total_words += len(text.split())

        # Progress indicator
        if (page_num + 1) % 25 == 0 or page_num == 0:
            print(f"  ... page {page_num + 1}/{page_count} ({total_words:,} words so far)")

    doc.close()
    return pages, total_words, page_count


def pages_to_markdown(
    pages: list[tuple[int, str]],
    title: str,
    word_count: int,
    page_count: int,
    source_file: str,
    elapsed: float,
) -> str:
    """Convert OCR'd pages to a formatted Markdown document."""
    lines = []

    lines.append(f"# {title}")
    lines.append("")
    lines.append(f"> **Source**: `{source_file}`  ")
    lines.append(f"> **Pages**: {page_count}  ")
    lines.append(f"> **Word Count**: {word_count:,}  ")
    lines.append(f"> **Extracted via**: Tesseract OCR (local)  ")
    lines.append(f"> **Processing time**: {elapsed:.1f}s  ")
    lines.append("")
    lines.append("---")
    lines.append("")

    for page_num, text in pages:
        lines.append(f"## Page {page_num}")
        lines.append("")
        cleaned = text.strip()
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        lines.append(cleaned)
        lines.append("")

    return "\n".join(lines)


def main():
    # Target the specific scanned PDF, or accept a path argument
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    output_dir = project_dir / "converted" / "pdf"
    output_dir.mkdir(parents=True, exist_ok=True)

    if len(sys.argv) >= 2:
        pdf_path = Path(sys.argv[1])
    else:
        # Default: the one scanned PDF that was skipped
        pdf_path = project_dir / "Too long" / "Options Essential Concepts and Trading Strategies, 2nd Edition.pdf"

    if not pdf_path.exists():
        print(f"File not found: {pdf_path}")
        sys.exit(1)

    print(f"OCR conversion: {pdf_path.name}")
    print(f"This is a {fitz.open(str(pdf_path)).page_count}-page scanned PDF — this will take a few minutes.\n")

    start = time.time()
    pages, word_count, page_count = ocr_pdf(str(pdf_path))
    elapsed = time.time() - start

    if word_count == 0:
        print(f"\nNo text could be extracted even with OCR. The PDF may be protected or corrupted.")
        sys.exit(1)

    # Build output filename
    safe_name = re.sub(r'[^\w\s\-]', '', pdf_path.stem).strip()
    safe_name = re.sub(r'\s+', '-', safe_name).lower()
    md_filename = f"{safe_name}.md"
    md_path = output_dir / md_filename

    try:
        relative = pdf_path.relative_to(project_dir)
    except ValueError:
        relative = pdf_path.name

    md_content = pages_to_markdown(pages, pdf_path.stem, word_count, page_count, str(relative), elapsed)
    md_path.write_text(md_content, encoding="utf-8")

    print(f"\n{'=' * 70}")
    print(f"DONE in {elapsed:.1f}s")
    print(f"  Pages:      {page_count:,}")
    print(f"  Words:      {word_count:,}")
    print(f"  Output:     {md_path}")
    print(f"  Speed:      {page_count / elapsed:.1f} pages/sec")


if __name__ == "__main__":
    main()
