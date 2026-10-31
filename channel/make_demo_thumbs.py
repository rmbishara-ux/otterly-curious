"""Vertical thumbnails for the demo ("Try this at home") Shorts, same look as the Gus-Short thumbnails.
Art: the episode's experiment still (episodes/EXX/shots/<shot>.png). python3 channel/make_demo_thumbs.py"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pipeline.common import font_path
OUT = ROOT / "channel" / "demo_thumbs"
W, H = 1080, 1920
NAVY, YEL, WHITE = (24, 44, 84), (255, 214, 64), (255, 255, 255)
# ep: (still, crop centre as fraction of width, headline lines, zoom)
SPEC = {
    "E01": ("E01-S038", 0.44, [("WHERE DID THE", WHITE), ("WATER GO?", YEL)], 1.0),
    "E02": ("E02-S038", 0.47, [("WHY HOLD", WHITE), ("HANDS?", YEL)], 1.0),
    "E03": ("E03-S043", 0.47, [("MAKE A", WHITE), ("RAINBOW!", YEL)], 1.0),
    "E04": ("E04-S040", 0.50, [("WHY DO BOATS", WHITE), ("FLOAT?", YEL)], 1.0),
    "E05": ("E05-S036", 0.64, [("WATCH A SEED", WHITE), ("WAKE UP!", YEL)], 1.0),
}

def fit(d, text, maxw, size):
    while size > 40 and d.textlength(text, font=ImageFont.truetype(font_path(), size)) > maxw:
        size -= 4
    return size

def headline(base, lines):
    d = ImageDraw.Draw(base)
    size = min(fit(d, t, W - 110, 190) for t, _ in lines)
    f = ImageFont.truetype(font_path(), size)
    sh = Image.new("RGBA", base.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(sh); y = 130
    for t, _ in lines:
        x = (W - d.textlength(t, font=f)) / 2
        sd.text((x + 8, y + 10), t, font=f, fill=(0, 0, 0, 150), stroke_width=18, stroke_fill=(0, 0, 0, 150)); y += int(size * 1.05)
    base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8))); y = 130
    for t, c in lines:
        x = (W - d.textlength(t, font=f)) / 2
        d.text((x, y), t, font=f, fill=c, stroke_width=14, stroke_fill=NAVY); y += int(size * 1.05)

def pill(base, text, y, size, fill, outline_w):
    d = ImageDraw.Draw(base); f = ImageFont.truetype(font_path(), size)
    w = d.textlength(text, font=f); x = (W - w) / 2; pad = size * 0.6
    d.rounded_rectangle((x - pad, y - size * 0.25, x + w + pad, y + size * 1.2), int(size * 0.7), fill=fill, outline=NAVY, width=outline_w)
    d.text((x, y), text, font=f, fill=NAVY)

OUT.mkdir(parents=True, exist_ok=True)
for ep, (shot, cx, lines, zoom) in SPEC.items():
    src = Image.open(ROOT / "episodes" / ep / "shots" / f"{shot}.png").convert("RGBA")
    sw, shh = src.size
    ch = int(shh / zoom); cw = int(ch * W / H)
    left = max(0, min(sw - cw, int(cx * sw - cw / 2))); top = (shh - ch) // 2
    im = src.crop((left, top, left + cw, top + ch)).resize((W, H), Image.LANCZOS)
    im = ImageEnhance.Color(im.convert("RGB")).enhance(1.08).convert("RGBA")
    # soft dark band at the top so the headline reads on bright skies
    g = Image.linear_gradient("L").resize((W, 700)).transpose(Image.FLIP_TOP_BOTTOM)
    band = Image.new("RGBA", (W, 700), (10, 25, 60, 0)); band.putalpha(g.point(lambda v: int(v * 0.45)))
    im.alpha_composite(band, (0, 0))
    headline(im, lines)
    pill(im, "TRY THIS AT HOME!", H - 330, 66, YEL + (255,), 6)
    pill(im, "OTTERLY CURIOUS", H - 190, 44, (255, 255, 255, 235), 5)
    im = im.convert("RGB")
    im.save(OUT / f"{ep}_short_demo_thumb.jpg", "JPEG", quality=90, optimize=True)
    print(ep, (OUT / f"{ep}_short_demo_thumb.jpg").stat().st_size)
