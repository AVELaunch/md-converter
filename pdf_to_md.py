#!/usr/bin/env python3
"""
PDF to Markdown Converter
Converts all PDF files in a directory to Markdown with word count summaries.
"""

import os
import sys
import re
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    print("PyMuPDF not installed. Installing...")
    os.system(f"{sys.executable} -m pip install PyMuPDF")
    import fitz


def extract_text_from_pdf(pdf_path: str) -> tuple[str, int, int]:
    """Extract text from a PDF file. Returns (pages, word_count, page_count)."""
    doc = fitz.open(pdf_path)
    pages = []
    total_words = 0
    page_count = len(doc)

    for page_num in range(page_count):
        page = doc[page_num]
        text = page.get_text("text")
        if text.strip():
            pages.append((page_num + 1, text))
            total_words += len(text.split())

    doc.close()
    return pages, total_words, page_count


def pages_to_markdown(pages: list[tuple[int, str]], title: str, word_count: int, page_count: int, source_file: str) -> str:
    """Convert extracted pages to a formatted Markdown document."""
    lines = []

    # Header with metadata
    lines.append(f"# {title}")
    lines.append("")
    lines.append(f"> **Source**: `{source_file}`  ")
    lines.append(f"> **Pages**: {page_count}  ")
    lines.append(f"> **Word Count**: {word_count:,}  ")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Content by page
    for page_num, text in pages:
        lines.append(f"## Page {page_num}")
        lines.append("")

        # Clean up the text
        cleaned = text.strip()
        # Collapse excessive blank lines
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)

        lines.append(cleaned)
        lines.append("")

    return "\n".join(lines)


def convert_pdfs(source_dir: str, output_dir: str):
    """Find and convert all PDFs in source_dir, saving to output_dir."""
    source_path = Path(source_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    pdf_files = sorted(source_path.rglob("*.pdf"))

    if not pdf_files:
        print("No PDF files found.")
        return

    print(f"Found {len(pdf_files)} PDF file(s)\n")
    print(f"{'File':<60} {'Pages':>6} {'Words':>10} {'Status'}")
    print("-" * 90)

    results = []

    for pdf_file in pdf_files:
        name = pdf_file.stem
        relative = pdf_file.relative_to(source_path)
        display_name = str(relative)[:57] + "..." if len(str(relative)) > 60 else str(relative)

        try:
            pages, word_count, page_count = extract_text_from_pdf(str(pdf_file))

            if word_count == 0:
                status = "SKIPPED (no text - possibly scanned)"
                print(f"{display_name:<60} {page_count:>6} {word_count:>10,} {status}")
                results.append((str(relative), page_count, word_count, status))
                continue

            # Build safe output filename
            safe_name = re.sub(r'[^\w\s\-]', '', name).strip()
            safe_name = re.sub(r'\s+', '-', safe_name).lower()
            md_filename = f"{safe_name}.md"
            md_path = output_path / md_filename

            # Convert to markdown
            md_content = pages_to_markdown(pages, name, word_count, page_count, str(relative))

            md_path.write_text(md_content, encoding="utf-8")

            status = f"OK -> {md_filename}"
            print(f"{display_name:<60} {page_count:>6} {word_count:>10,} {status}")
            results.append((str(relative), page_count, word_count, status))

        except Exception as e:
            status = f"ERROR: {e}"
            print(f"{display_name:<60} {'?':>6} {'?':>10} {status}")
            results.append((str(relative), 0, 0, status))

    # Summary
    total_files = len([r for r in results if "OK" in r[3]])
    total_words = sum(r[2] for r in results)
    total_pages = sum(r[1] for r in results)

    print("\n" + "=" * 90)
    print(f"SUMMARY: {total_files}/{len(pdf_files)} files converted | {total_pages:,} pages | {total_words:,} total words")
    print(f"Output directory: {output_path.resolve()}")


if __name__ == "__main__":
    # Default paths
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    output_dir = project_dir / "converted" / "pdf"

    # Allow override via command line
    if len(sys.argv) >= 2:
        project_dir = Path(sys.argv[1])
    if len(sys.argv) >= 3:
        output_dir = Path(sys.argv[2])

    convert_pdfs(str(project_dir), str(output_dir))
