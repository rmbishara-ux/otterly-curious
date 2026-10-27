"""Thumbnail v2: dedicated scene art + short bold headline. python3 channel/make_thumbs_v2.py"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pipeline.common import font_path
RAW = ROOT / "channel" / "thumbs_v2" / "raw"; OUT = ROOT / "channel" / "thumbs_v2"
W, H = 1280, 720
NAVY, YEL, WHITE = (24, 44, 84), (255, 214, 64), (255, 255, 255)
# ep: (art, [(line, color)], x, y, size)
SPEC = {
    "E01": ("E01_A", [("WHERE DID THE", WHITE), ("WATER GO?", YEL)], 40, 64, 96),
    "E02": ("E02_B", [("WHY HOLD", WHITE), ("HANDS?", YEL)], 40, 56, 112),
    "E05": ("E05_A", [("WHAT DOES", WHITE), ("A SEED", YEL), ("NEED?", WHITE)], 40, 200, 80),
    "E03": ("E03_A", [("WHERE DO", WHITE), ("RAINBOWS", YEL), ("COME FROM?", WHITE)], 44, 330, 92),
}
def draw_text(base, lines, x, y, size):
    f = ImageFont.truetype(font_path(), size)
    sh = Image.new("RGBA", base.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
    yy = y
    for t, c in lines:
        sd.text((x + 6, yy + 8), t, font=f, fill=(0, 0, 0, 150), stroke_width=14, stroke_fill=(0, 0, 0, 150)); yy += int(size * 1.05)
    base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
    d = ImageDraw.Draw(base); yy = y
    for t, c in lines:
        d.text((x, yy), t, font=f, fill=c, stroke_width=11, stroke_fill=NAVY); yy += int(size * 1.05)
    return base
def tag(base):
    d = ImageDraw.Draw(base); f = ImageFont.truetype(font_path(), 34); t = "OTTERLY CURIOUS"
    w = int(d.textlength(t, font=f)); x, y = 40, H - 78
    d.rounded_rectangle((x - 18, y - 8, x + w + 18, y + 52), 28, fill=(255, 255, 255, 235), outline=NAVY, width=4)
    d.text((x, y), t, font=f, fill=NAVY)
    return base
for ep, (art, lines, x, y, size) in SPEC.items():
    im = Image.open(RAW / f"{art}.png").convert("RGBA").resize((W, H), Image.LANCZOS)
    im = tag(draw_text(im, lines, x, y, size)).convert("RGB")
    im.save(OUT / f"{ep}_thumb_v2.png"); im.save(OUT / f"{ep}_thumb_v2.jpg", "JPEG", quality=90, optimize=True)
    print(ep, (OUT / f"{ep}_thumb_v2.jpg").stat().st_size)
