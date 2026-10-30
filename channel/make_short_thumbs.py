"""Vertical thumbnails for the Gus (fail) Shorts, matching the demo-Short style.
Source art: the Gus shot's still from episodes/EXX/image_ledger.json, saved to channel/short_thumbs/raw/.
python3 channel/make_short_thumbs.py
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pipeline.common import font_path
RAW = ROOT / "channel" / "short_thumbs" / "raw"; OUT = ROOT / "channel" / "short_thumbs"
W, H = 1080, 1920
NAVY, YEL, WHITE = (24, 44, 84), (255, 214, 64), (255, 255, 255)
# ep: (shot, crop centre as fraction of source width, headline lines[, px to push art down so the headline clears Gus])
SPEC = {
    "E01": ("E01-S030", 0.44, [("SPLASH!", YEL)]),
    "E02": ("E02-S028", 0.40, [("WHERE", WHITE), ("AM I?", YEL)]),
    "E03": ("E03-S027", 0.47, [("MY", WHITE), ("RAINBOW!", YEL)]),
    "E04": ("E04-S027", 0.39, [("WILL IT", WHITE), ("FLOAT?", YEL)], 360),
    "E05": ("E05-S026", 0.36, [("IS IT A", WHITE), ("TREE YET?", YEL)]),
}


def fit(d, text, maxw, size):
    while size > 40 and d.textlength(text, font=ImageFont.truetype(font_path(), size)) > maxw:
        size -= 4
    return size


def headline(base, lines):
    d = ImageDraw.Draw(base)
    size = min(fit(d, t, W - 120, 210) for t, _ in lines)
    f = ImageFont.truetype(font_path(), size)
    sh = Image.new("RGBA", base.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
    y = 120
    for t, _ in lines:
        x = (W - d.textlength(t, font=f)) / 2
        sd.text((x + 8, y + 10), t, font=f, fill=(0, 0, 0, 150), stroke_width=18, stroke_fill=(0, 0, 0, 150)); y += int(size * 1.05)
    base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)))
    y = 120
    for t, c in lines:
        x = (W - d.textlength(t, font=f)) / 2
        d.text((x, y), t, font=f, fill=c, stroke_width=14, stroke_fill=NAVY); y += int(size * 1.05)


def pill(base, text, y, size, fill, outline_w):
    d = ImageDraw.Draw(base); f = ImageFont.truetype(font_path(), size)
    w = d.textlength(text, font=f); x = (W - w) / 2; pad = size * 0.6
    d.rounded_rectangle((x - pad, y - size * 0.25, x + w + pad, y + size * 1.2), int(size * 0.7), fill=fill, outline=NAVY, width=outline_w)
    d.text((x, y), text, font=f, fill=NAVY)


OUT.mkdir(parents=True, exist_ok=True)
for ep, (shot, cx, lines, *rest) in SPEC.items():
    drop = rest[0] if rest else 0
    src = Image.open(RAW / f"{shot}.png").convert("RGBA")
    sw, shh = src.size
    cw = int(shh * W / H)
    left = max(0, min(sw - cw, int(cx * sw - cw / 2)))
    im = src.crop((left, 0, left + cw, shh)).resize((W, H), Image.LANCZOS)
    if drop:  # push art down; fill the gap with a blurred stretch of the sky
        bg = im.crop((0, 0, W, drop + 200)).resize((W, drop + 200)).filter(ImageFilter.GaussianBlur(30))
        moved = Image.new("RGBA", (W, H)); moved.paste(bg, (0, 0)); moved.alpha_composite(im.crop((0, 0, W, H - drop)), (0, drop))
        fade = Image.linear_gradient("L").resize((W, 160))
        top = im.crop((0, 0, W, 160)); moved.paste(bg.crop((0, drop, W, drop + 160)), (0, drop), Image.eval(fade, lambda v: 255 - v))
        im = moved
    headline(im, lines)
    pill(im, "GUS HAS A FASTER WAY!", H - 330, 66, YEL + (255,), 6)
    pill(im, "OTTERLY CURIOUS", H - 190, 44, (255, 255, 255, 235), 5)
    im = im.convert("RGB")
    im.save(OUT / f"{ep}_short_fail_thumb.png")
    im.save(OUT / f"{ep}_short_fail_thumb.jpg", "JPEG", quality=90, optimize=True)
    print(ep, (OUT / f"{ep}_short_fail_thumb.jpg").stat().st_size)
