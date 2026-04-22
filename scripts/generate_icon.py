from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import os, sys

FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/HelveticaNeue.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]
font_path = next((p for p in FONT_CANDIDATES if os.path.exists(p)), None)
if not font_path:
    sys.exit("No usable bold font found")

BG = (30, 41, 59, 255)
FG = (255, 255, 255, 255)
ACCENT = (56, 189, 248, 255)

def make_icon(size):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([(0, 0), (size, size)], radius=int(size * 0.22), fill=BG)
    text_font = ImageFont.truetype(font_path, int(size * 0.30))
    arrow_font = ImageFont.truetype(font_path, int(size * 0.36))
    md_bbox = draw.textbbox((0, 0), "MD", font=text_font)
    md_w, md_h = md_bbox[2]-md_bbox[0], md_bbox[3]-md_bbox[1]
    arrow = "\u2193"
    a_bbox = draw.textbbox((0, 0), arrow, font=arrow_font)
    a_w, a_h = a_bbox[2]-a_bbox[0], a_bbox[3]-a_bbox[1]
    dot_size = int(size * 0.08)
    dot_gap = int(size * 0.02)
    arrow_gap = int(size * 0.025)
    total_w = dot_size + dot_gap + md_w + arrow_gap + a_w
    start_x = (size - total_w) // 2
    center_y = size // 2
    md_top = center_y - md_h // 2
    md_bottom = md_top + md_h
    dot_x = start_x
    dot_y = md_bottom - dot_size
    draw.rounded_rectangle(
        [(dot_x, dot_y), (dot_x + dot_size, dot_y + dot_size)],
        radius=int(dot_size * 0.15), fill=FG,
    )
    md_x = dot_x + dot_size + dot_gap - md_bbox[0]
    md_y = center_y - md_h // 2 - md_bbox[1]
    draw.text((md_x, md_y), "MD", font=text_font, fill=FG)
    a_x = md_x + md_w + arrow_gap - a_bbox[0]
    a_y = center_y - a_h // 2 - a_bbox[1]
    draw.text((a_x, a_y), arrow, font=arrow_font, fill=ACCENT)
    return img

out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("assets/icon.iconset")
out_dir.mkdir(parents=True, exist_ok=True)
for size, name in [
    (16, "icon_16x16.png"), (32, "icon_16x16@2x.png"),
    (32, "icon_32x32.png"), (64, "icon_32x32@2x.png"),
    (128, "icon_128x128.png"), (256, "icon_128x128@2x.png"),
    (256, "icon_256x256.png"), (512, "icon_256x256@2x.png"),
    (512, "icon_512x512.png"), (1024, "icon_512x512@2x.png"),
]:
    make_icon(size).save(out_dir / name)
print(f"Wrote {len(list(out_dir.iterdir()))} icon files to {out_dir}")
