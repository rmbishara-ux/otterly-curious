"""Stage 9: YouTube packaging (title, description, tags, chapters, made-for-kids flag) and thumbnail."""
import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from .common import ROOT, ep_dir, font_path, read_json
from .script_format import parse
from .stages import load_sb

BASE_TAGS = ["science for kids", "kids science", "kids learning videos", "educational videos for kids", "preschool science",
             "Otterly Curious", "animated stories for kids", "learn with otters", "kids cartoon"]


def title_for(meta):
    t = f"{meta['big_question']} | Otterly Curious"
    assert len(t) < 60, f"title too long ({len(t)}): {t}"
    return t


def chapters(sb):
    t, first, out = 0.0, {}, []
    for s in sb["shots"]:
        first.setdefault(s["beat"], t)
        t += s["duration"]
    names = {1: "Big question", 2: "Theme song", 3: "Let's guess", 4: "Uh-oh!", 5: "Let's find out", 6: "Try it out", 7: "Wonder Pocket"}
    for b in sorted(first):
        m, sec = divmod(int(first[b]), 60)
        out.append(f"{m}:{sec:02d} {names[b]}")
    if not out[0].startswith("0:00"):
        out[0] = "0:00 " + out[0].split(" ", 1)[1]
    return out


def thumbnail(ep, meta, out):
    W, H = 1280, 720
    d = ep_dir(ep)
    loc = next((s["location"] for s in (load_sb(ep)["shots"]) if s["beat"] == 3), "driftwood_playground")
    plate = ROOT / "bible" / "locations" / f"{loc}.png"
    bg = Image.open(plate).convert("RGB").resize((W, H)) if plate.exists() else Image.new("RGB", (W, H), (190, 220, 245))
    blend = 0.35
    hs = d / "hero_shots.json"
    if hs.exists() and ep != "E01":  # E02 onward: the episode's first hero frame (e.g. the rainbow) is a stronger backdrop than the plain plate
        import json as _j
        still = d / "shots" / f"{ep}-{_j.loads(hs.read_text())[0]}.png"
        if still.exists():
            bg = Image.open(still).convert("RGB")
            lay = d / "thumb_layout.json"  # optional per-episode crop (fractions x0,y0,x1,y1) so the key subject stays visible
            if lay.exists():
                x0, y0, x1, y1 = _j.loads(lay.read_text())["crop"]
                bg = bg.crop((int(bg.width * x0), int(bg.height * y0), int(bg.width * x1), int(bg.height * y1)))
            bg = bg.resize((W, H))
            blend = 0.12
    bg = Image.blend(bg, Image.new("RGB", (W, H), (255, 255, 255)), blend)
    sheet = ROOT / "characters" / "ollie" / "expressions" / "expr_v2.png"
    if sheet.exists():
        s = Image.open(sheet).convert("RGB")
        pw, ph = s.width // 3, s.height // 2
        face = s.crop((8, 8, pw - 8, ph - 8))
        face = face.resize((int(face.width * H / face.height), H))
        cx = face.width // 2
        face = face.crop((max(0, cx - int(W * 0.25)), 0, max(0, cx - int(W * 0.25)) + int(W * 0.5), H))
        bg.paste(face, (0, 0))
    dr = ImageDraw.Draw(bg)
    q = meta["big_question"]
    size = 104
    fnt = ImageFont.truetype(font_path(), size)
    maxw = int(W * 0.46)
    words, lines, cur = q.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if dr.textlength(test, font=fnt) <= maxw:
            cur = test
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    y = (H - len(lines) * (size + 8)) // 2
    lay = d / "thumb_layout.json"
    if lay.exists():
        import json as _k
        ty = _k.loads(lay.read_text()).get("text_y")
        if ty:
            y = ty
    for ln in lines:
        dr.text((int(W * 0.51), y), ln, font=fnt, fill=(255, 255, 255), stroke_width=8, stroke_fill=(29, 53, 87))
        y += size + 8
    bg.save(out)


def package(ep):
    d = ep_dir(ep)
    meta, _ = parse(d / "script.md")
    sb = load_sb(ep)
    title = title_for(meta)
    ch = chapters(sb)
    topic = meta["big_question"].rstrip("?").lower()
    desc = (f"TRY IT AT HOME: {meta['demo_steps']}\n\n"
            f"In this episode of Otterly Curious, Ollie the sea otter and his friends ask: {meta['big_question']} "
            f"{meta.get('science', '')} Along the way, Gus learns about {meta['value'].lower()}.\n\n"
            f"A science-for-kids story for ages 3-7, made to be watched together.\n\n" + "\n".join(ch) +
            "\n\nSubscribe to Otterly Curious for a new question every week.")
    tags = BASE_TAGS + [topic, f"{topic} for kids", f"learn about {meta['value'].lower()}"]
    final = (d / "renders" / f"{ep}_episode.mp4").exists()
    est = "" if final else "\n> NOTE: chapter times are estimates from the storyboard; regenerate after the final render.\n"
    md = (f"# {ep} YouTube package\n\n**Title** ({len(title)} chars): {title}\n\n**Made for kids:** YES (required, no exceptions)\n"
          f"**Comments:** disabled by the made-for-kids setting. **Captions:** upload final/captions.srt (from the script, not auto).\n"
          f"**End screens/links/QR/merch:** none.\n\n## Description{est}\n{desc}\n\n## Tags\n{', '.join(tags)}\n\n"
          f"## Shorts\n- Demo Short (45-60 s): `final/{ep}_short_demo.mp4`, title: Try this at home: {meta['big_question']}\n"
          f"- Fail Short (20-30 s): `final/{ep}_short_fail.mp4`, title: Gus has a faster way! #Shorts\n\n"
          f"## Audit\nScript v1 in script.md; assets logged in logs/{ep}_generations.jsonl; QA in qa_report.md.\n")
    (d / "youtube.md").write_text(md)
    thumbnail(ep, meta, d / "final" / f"{ep}_thumbnail.png")
    return title
