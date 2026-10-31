"""Trailer thumbnail: Ollie waving (frame from lipsync/T_hi.mp4) pushed right, title on the left. python3 channel/make_trailer_thumb.py"""
import subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
ROOT = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(ROOT))
from pipeline.common import font_path
T = ROOT / "channel" / "trailer"; NAVY, YEL, WHITE = (24, 44, 84), (255, 214, 64), (255, 255, 255); W, H, SHIFT = 1280, 720, 330
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "1.9", "-i", str(T / "lipsync" / "T_hi.mp4"), "-frames:v", "1", str(T / "thumb_src.png")], check=True)
src = Image.open(T / "thumb_src.png").convert("RGBA").resize((W, H), Image.LANCZOS)
im = src.crop((0, 0, W - SHIFT, H)).resize((W, H)).filter(ImageFilter.GaussianBlur(22))  # soft backdrop behind the title
fg = src.crop((0, 0, W - SHIFT, H)); m = Image.new("L", fg.size, 255); md = ImageDraw.Draw(m)
for i in range(220): md.line([(i, 0), (i, H)], fill=int(255 * i / 220))  # fade the art in over 220 px
im.paste(fg, (SHIFT, 0), m)
lines, size, x, y = [("MEET", WHITE), ("OTTERLY", YEL), ("CURIOUS!", YEL)], 104, 44, 140
f = ImageFont.truetype(font_path(), size); sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(sh); yy = y
for t, c in lines: sd.text((x + 6, yy + 8), t, font=f, fill=(0, 0, 0, 150), stroke_width=14, stroke_fill=(0, 0, 0, 150)); yy += int(size * 1.05)
im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6))); d = ImageDraw.Draw(im); yy = y
for t, c in lines: d.text((x, yy), t, font=f, fill=c, stroke_width=11, stroke_fill=NAVY); yy += int(size * 1.05)
f2 = ImageFont.truetype(font_path(), 34); t = "SCIENCE STORIES FOR KIDS"; w = d.textlength(t, font=f2); py = yy + 22
d.rounded_rectangle((x - 4, py - 10, x + w + 30, py + 50), 26, fill=YEL + (255,), outline=NAVY, width=5); d.text((x + 13, py), t, font=f2, fill=NAVY)
im.convert("RGB").save(T / "trailer_thumb.jpg", "JPEG", quality=90); print(T / "trailer_thumb.jpg")
