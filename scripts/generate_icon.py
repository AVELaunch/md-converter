#!/usr/bin/env python3
"""Generate a macOS .icns icon for the MD Converter app."""

import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def create_icon_png(size: int = 1024) -> Image.Image:
    """Create a clean icon: dark rounded rect with white 'MD' text and arrow."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Dark rounded rectangle background (#1e1e2e)
    margin = int(size * 0.05)
    radius = int(size * 0.18)
    draw.rounded_rectangle(
        [margin, margin, size - margin, size - margin],
        radius=radius,
        fill=(30, 30, 46, 255),
    )

    # "MD" text - large, centered, white
    md_font_size = int(size * 0.35)
    try:
        md_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", md_font_size)
    except (OSError, IOError):
        md_font = ImageFont.load_default()

    md_text = "MD"
    md_bbox = draw.textbbox((0, 0), md_text, font=md_font)
    md_w = md_bbox[2] - md_bbox[0]
    md_h = md_bbox[3] - md_bbox[1]
    md_x = (size - md_w) // 2
    md_y = (size - md_h) // 2 - int(size * 0.06)
    draw.text((md_x, md_y), md_text, fill=(255, 255, 255, 255), font=md_font)

    # Conversion arrow below the text (a simple right-pointing arrow)
    arrow_y = md_y + md_h + int(size * 0.06)
    arrow_cx = size // 2
    arrow_len = int(size * 0.20)
    arrow_head = int(size * 0.04)
    line_width = max(int(size * 0.02), 3)
    arrow_color = (166, 173, 200, 255)  # #a6adc8

    # Arrow shaft
    draw.line(
        [(arrow_cx - arrow_len // 2, arrow_y), (arrow_cx + arrow_len // 2, arrow_y)],
        fill=arrow_color,
        width=line_width,
    )
    # Arrow head (triangle)
    tip_x = arrow_cx + arrow_len // 2
    draw.polygon(
        [
            (tip_x, arrow_y - arrow_head),
            (tip_x + arrow_head + 2, arrow_y),
            (tip_x, arrow_y + arrow_head),
        ],
        fill=arrow_color,
    )

    # Small label below arrow
    label_size = int(size * 0.08)
    try:
        label_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", label_size)
    except (OSError, IOError):
        label_font = ImageFont.load_default()

    label = "CONVERTER"
    lb = draw.textbbox((0, 0), label, font=label_font)
    lw = lb[2] - lb[0]
    draw.text(
        ((size - lw) // 2, arrow_y + int(size * 0.04)),
        label,
        fill=(108, 112, 134, 255),  # #6c7086
        font=label_font,
    )

    return img


def png_to_icns(png_path: Path, icns_path: Path):
    """Convert a 1024x1024 PNG to .icns using macOS iconutil."""
    with tempfile.TemporaryDirectory() as tmpdir:
        iconset = Path(tmpdir) / "icon.iconset"
        iconset.mkdir()

        img = Image.open(png_path)

        # Required icon sizes for macOS .iconset
        sizes = [16, 32, 64, 128, 256, 512, 1024]
        for s in sizes:
            resized = img.resize((s, s), Image.LANCZOS)
            resized.save(iconset / f"icon_{s}x{s}.png")
            # @2x variants
            if s <= 512:
                resized2x = img.resize((s * 2, s * 2), Image.LANCZOS)
                resized2x.save(iconset / f"icon_{s}x{s}@2x.png")

        # Rename 1024 to 512@2x (required by iconutil)
        src_1024 = iconset / "icon_1024x1024.png"
        dst_512_2x = iconset / "icon_512x512@2x.png"
        if src_1024.exists() and not dst_512_2x.exists():
            src_1024.rename(dst_512_2x)
        elif src_1024.exists():
            src_1024.unlink()

        result = subprocess.run(
            ["iconutil", "-c", "icns", str(iconset), "-o", str(icns_path)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"iconutil failed: {result.stderr}")


def main():
    scripts_dir = Path(__file__).resolve().parent
    png_path = scripts_dir / "icon.png"
    icns_path = scripts_dir / "icon.icns"

    print("Generating 1024x1024 icon PNG...")
    icon = create_icon_png(1024)
    icon.save(str(png_path), "PNG")
    print(f"  Saved: {png_path}")

    print("Converting to .icns...")
    png_to_icns(png_path, icns_path)
    print(f"  Saved: {icns_path}")


if __name__ == "__main__":
    main()
