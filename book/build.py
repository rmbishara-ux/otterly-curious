#!/usr/bin/env python3
"""python3 book/build.py E01 -> episodes/E01/book/out/{E01_print.pdf, E01_ebook.pdf, E01.epub, validation.md}

Layout: 32 pages, 8.5 x 8.5 in trim, 0.125 in bleed (print PDF page = 8.75 in square). Page plan:
1 cover | 2 title | 3 copyright | 4-29 thirteen story spreads | 30 Wonder Pocket | 31 Try it at home | 32 back cover.
Art per spread: episodes/EXX/book/art/spread_NN.png (2:1, print-res) if present, else the storyboard still, else the location plate (placeholder)."""
import json, sys, zipfile, textwrap, re
from pathlib import Path
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pipeline.common import ROOT, ep_dir, ttf_font_path as font_path, read_json

SENT_RE = r'[.!?]+["\u201d]?(?:\s+(?!\w+(?:\s\w+)?\s(?:said|asked|whispered|cried|called|squawked|gasped|admitted|laughed|giggled))(?=["\u201cA-Z])|\s*$)'
IN = 72.0
TRIM, BLEED = 8.5 * IN, 0.125 * IN
PAGE = TRIM + 2 * BLEED
SAFE = BLEED + 0.5 * IN  # text stays 0.5in inside the trim edge


def fonts():
    pdfmetrics.registerFont(TTFont("Body", font_path()))
    return "Body"


def art_for(ep, i, sp, sb):
    d = ep_dir(ep) / "book" / "art"
    p = d / f"spread_{i:02d}.png"
    if p.exists():
        return Image.open(p).convert("RGB"), "print-res art"
    shot = next((s for s in sb["shots"] if s["id"] == sp["shot_hint"]), None) if sb else None
    if shot:
        still = ep_dir(ep) / "shots" / f"{shot['id']}.png"
        if still.exists():
            return Image.open(still).convert("RGB"), "storyboard still (needs print-res regeneration)"
        plate = ROOT / "bible" / "locations" / f"{shot['location']}.png"
        if plate.exists():
            return Image.open(plate).convert("RGB"), "location plate placeholder (needs episode art)"
    return Image.new("RGB", (2000, 1000), (190, 220, 245)), "blank placeholder"


def fit_2to1(im):
    w, h = im.size
    target = 2.0
    if w / h > target:
        nw = int(h * target)
        im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    else:
        nh = int(w / target)
        im = im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
    return im


def draw_text_box(c, font, text, x, y, w, size=22, lead=30, fill=(0.96, 0.92, 0.85), alpha=0.92):
    chars = max(10, int(w / (size * 0.52)))
    lines = []
    for para in text.split("\n"):
        lines += textwrap.wrap(para, chars) or [""]
    h = len(lines) * lead + 36
    c.saveState()
    c.setFillColorRGB(*fill)
    c.setFillAlpha(alpha)
    c.roundRect(x - 18, y - h + 18, w + 36, h, 22, fill=1, stroke=0)
    c.restoreState()
    c.setFillColorRGB(0.11, 0.21, 0.34)
    c.setFont(font, size)
    ty = y - 12
    for ln in lines:
        c.drawString(x, ty, ln)
        ty -= lead
    return h


def page_art(c, im, px, bleed_full=True):
    c.drawImage(ImageReader(im), px, 0, width=PAGE, height=PAGE)


def build(ep):
    book = json.loads((ep_dir(ep) / "book" / "book.json").read_text())
    sb = read_json(ep_dir(ep) / "storyboard.json")
    font = fonts()
    out = ep_dir(ep) / "book" / "out"
    out.mkdir(exist_ok=True)
    words = sum(len(re.findall(r"[A-Za-z']+", s["text"])) for s in book["spreads"])
    notes = [f"Story text: {words} words (target 500-800): {'OK' if 500 <= words <= 800 else 'OUT OF RANGE'}"]
    sentences = [len(re.findall(SENT_RE, s["text"])) for s in book["spreads"]]
    notes.append(f"Sentences per spread: min {min(sentences)}, max {max(sentences)} (target 1-3): " + ("OK" if max(sentences) <= 3 else "OVER 3"))
    assert len(book["spreads"]) == 13
    beats = [s["beat"] for s in book["spreads"]]
    exp = {1: 1, 3: 3, 4: 2, 5: 4, 6: 2, 7: 1}
    notes.append("Beat mapping 1/3/2/4/2/1: " + ("OK" if all(beats.count(k) == v for k, v in exp.items()) else "MISMATCH"))

    def render(path, bleed):
        pg = PAGE if bleed else TRIM
        off = 0 if bleed else BLEED
        c = canvas.Canvas(str(path), pagesize=(pg, pg))
        c.setTitle(book["title"])
        c.setAuthor("Otterly Curious")

        def new_page_bg(rgb=(0.86, 0.91, 0.97)):
            c.setFillColorRGB(*rgb)
            c.rect(0, 0, pg, pg, fill=1, stroke=0)

        def sc(v):  # shift coordinates when trimming bleed away
            return v - off

        # 1 cover
        new_page_bg()
        face = Image.open(ROOT / "characters" / "ollie" / "expressions" / "expr_v2.png").convert("RGB")
        pw, ph = face.width // 3, face.height // 2
        face = face.crop((8, 8, pw - 8, ph - 8))
        c.drawImage(ImageReader(face), sc(BLEED + 0.9 * IN), sc(BLEED + 1.6 * IN), width=5.6 * IN, height=5.6 * IN * face.height / face.width)
        c.setFillColorRGB(0.11, 0.21, 0.34)
        c.setFont(font, 20)
        c.drawCentredString(pg / 2, sc(PAGE - SAFE - 6), book["series_line"])
        c.setFont(font, 36)
        for i, ln in enumerate(textwrap.wrap(book["title"], 22)):
            c.drawCentredString(pg / 2, sc(PAGE - SAFE - 56 - i * 42), ln)
        c.setFont(font, 22)
        c.drawCentredString(pg / 2, sc(SAFE + 8), book["subtitle"])
        c.showPage()
        # 2 title, 3 copyright
        new_page_bg((0.96, 0.92, 0.85))
        c.setFillColorRGB(0.11, 0.21, 0.34)
        c.setFont(font, 34)
        for i, ln in enumerate(textwrap.wrap(book["title"], 24)):
            c.drawCentredString(pg / 2, sc(PAGE / 2 + 40 - i * 44), ln)
        c.setFont(font, 18)
        c.drawCentredString(pg / 2, sc(PAGE / 2 - 60), book["series_line"])
        c.showPage()
        new_page_bg((0.96, 0.92, 0.85))
        c.setFillColorRGB(0.11, 0.21, 0.34)
        c.setFont(font, 11)
        y = sc(PAGE - SAFE - 20)
        for ln in textwrap.wrap(book["copyright"], 70):
            c.drawString(sc(SAFE), y, ln)
            y -= 16
        c.showPage()
        # 4-29 spreads
        for i, sp in enumerate(book["spreads"], 1):
            im, src = art_for(ep, i, sp, sb)
            im = fit_2to1(im)
            half = im.width // 2
            for side in (0, 1):
                part = im.crop((side * half, 0, (side + 1) * half, im.height))
                c.drawImage(ImageReader(part), sc(0), sc(0), width=PAGE, height=PAGE)
                if side == 0:
                    draw_text_box(c, font, sp["text"], sc(SAFE), sc(PAGE - SAFE), PAGE - 2 * SAFE, size=21, lead=28)
                c.showPage()
            if bleed:
                notes.append(f"spread {i}: art = {src}") if i == 1 or "print-res" not in src else None
        # 30 activity, 31 try it
        a = book["activity_page"]
        new_page_bg((0.99, 0.93, 0.78))
        c.setFillColorRGB(0.11, 0.21, 0.34)
        c.setFont(font, 32)
        c.drawCentredString(pg / 2, sc(PAGE - SAFE - 30), a["heading"])
        c.setFont(font, 21)
        y = sc(PAGE - SAFE - 100)
        for k, t in enumerate(a["learned"], 1):
            for j, ln in enumerate(textwrap.wrap(f"{k}. {t}", 44)):
                c.drawString(sc(SAFE + 10), y, ln)
                y -= 30
            y -= 12
        c.setFont(font, 22)
        y -= 20
        c.drawString(sc(SAFE + 10), y, "One kind thing to try today:")
        y -= 34
        c.drawString(sc(SAFE + 10), y, a["kind_thing"])
        c.showPage()
        t = book["try_page"]
        new_page_bg((0.86, 0.94, 0.98))
        c.setFillColorRGB(0.11, 0.21, 0.34)
        c.setFont(font, 32)
        c.drawCentredString(pg / 2, sc(PAGE - SAFE - 30), t["heading"])
        c.setFont(font, 20)
        y = sc(PAGE - SAFE - 90)
        for k, st in enumerate(t["steps"], 1):
            for ln in textwrap.wrap(f"{k}. {st}", 46):
                c.drawString(sc(SAFE + 10), y, ln)
                y -= 28
            y -= 8
        c.setFont(font, 14)
        y -= 14
        for ln in textwrap.wrap(t["note"], 68):
            c.drawString(sc(SAFE + 10), y, ln)
            y -= 19
        c.showPage()
        # 32 back
        new_page_bg()
        c.setFillColorRGB(0.11, 0.21, 0.34)
        c.setFont(font, 20)
        y = sc(PAGE - SAFE - 40)
        for ln in textwrap.wrap(book["blurb"], 40):
            c.drawString(sc(SAFE + 10), y, ln)
            y -= 28
        c.setFont(font, 16)
        c.drawCentredString(pg / 2, sc(SAFE + 70), "Every big question starts with \"Let's find out!\"")
        c.drawCentredString(pg / 2, sc(SAFE + 20), "(Reserve this area for the ISBN barcode if required.)")
        c.showPage()
        c.save()

    render(out / f"{ep}_print.pdf", bleed=True)
    render(out / f"{ep}_ebook.pdf", bleed=False)
    epub(ep, book, out, sb)
    # validation
    from pypdf import PdfReader  # noqa
    for name, size in ((f"{ep}_print.pdf", 8.75), (f"{ep}_ebook.pdf", 8.5)):
        r = PdfReader(str(out / name))
        w = float(r.pages[0].mediabox.width) / 72
        notes.append(f"{name}: {len(r.pages)} pages, {w:.3f} in square (expected {size}) -> {'OK' if len(r.pages) == 32 and abs(w - size) < 0.01 else 'FAIL'}")
    px_need = int(8.75 * 300)
    used_low = [1 + k for k, sp in enumerate(book["spreads"]) if not (ep_dir(ep) / "book" / "art" / f"spread_{k+1:02d}.png").exists()]
    notes.append(f"300 dpi check: each spread needs {2*px_need}x{px_need}px art in episodes/{ep}/book/art/spread_NN.png. Missing print-res art for spreads {used_low}: print PDF uses placeholders.")
    notes.append("Typeface: " + Path(font_path()).name + " (brief locks Nunito/Fredoka; drop the font into assets/fonts/ and rebuild).")
    (out / "validation.md").write_text("# Book validation\n\n" + "\n".join(f"- {n}" for n in notes) + "\n")
    print("\n".join(notes))


def epub(ep, book, out, sb):
    path = out / f"{ep}.epub"
    esc = lambda s: s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    items, spine, nav = [], [], []
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        z.writestr("META-INF/container.xml", '<?xml version="1.0"?><container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>')
        z.writestr("OEBPS/style.css", "body{font-family:sans-serif;color:#1d3557;margin:5%}img{width:100%}h1,h2{text-align:center}p{font-size:1.3em;line-height:1.5}")

        def page(fn, title, body):
            z.writestr(f"OEBPS/{fn}", f'<?xml version="1.0" encoding="utf-8"?><html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en"><head><title>{esc(title)}</title><link rel="stylesheet" href="style.css"/></head><body>{body}</body></html>')
            items.append((fn, f"id_{fn.split('.')[0]}", "application/xhtml+xml"))
            spine.append(f"id_{fn.split('.')[0]}")

        page("cover.xhtml", book["title"], f"<h1>{esc(book['title'])}</h1><h2>{esc(book['subtitle'])}</h2><p style='text-align:center'>{esc(book['series_line'])}</p>")
        nav.append(("cover.xhtml", "Cover"))
        for i, sp in enumerate(book["spreads"], 1):
            im, _ = art_for(ep, i, sp, sb)
            im = fit_2to1(im).resize((1600, 800))
            from io import BytesIO
            b = BytesIO()
            im.save(b, "JPEG", quality=85)
            z.writestr(f"OEBPS/img{i:02d}.jpg", b.getvalue())
            items.append((f"img{i:02d}.jpg", f"img{i:02d}", "image/jpeg"))
            page(f"s{i:02d}.xhtml", f"Spread {i}", f'<img src="img{i:02d}.jpg" alt="Illustration for page {i}"/><p>{esc(sp["text"])}</p>')
            nav.append((f"s{i:02d}.xhtml", f"Spread {i}"))
        a, t = book["activity_page"], book["try_page"]
        page("pocket.xhtml", a["heading"], f"<h2>{esc(a['heading'])}</h2><ol>" + "".join(f"<li>{esc(x)}</li>" for x in a["learned"]) + f"</ol><p>One kind thing to try today: {esc(a['kind_thing'])}</p>")
        nav.append(("pocket.xhtml", a["heading"]))
        page("tryit.xhtml", t["heading"], f"<h2>{esc(t['heading'])}</h2><ol>" + "".join(f"<li>{esc(x)}</li>" for x in t["steps"]) + f"</ol><p>{esc(t['note'])}</p>")
        nav.append(("tryit.xhtml", t["heading"]))
        navbody = "<nav epub:type='toc' xmlns:epub='http://www.idpf.org/2007/ops'><ol>" + "".join(f"<li><a href='{f}'>{esc(n)}</a></li>" for f, n in nav) + "</ol></nav>"
        z.writestr("OEBPS/nav.xhtml", f'<?xml version="1.0" encoding="utf-8"?><html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops"><head><title>Contents</title></head><body>{navbody}</body></html>')
        man = "".join(f'<item id="{i}" href="{f}" media-type="{m}"/>' for f, i, m in items)
        z.writestr("OEBPS/content.opf", f'<?xml version="1.0" encoding="utf-8"?><package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid"><metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:identifier id="uid">otterly-curious-{ep.lower()}</dc:identifier><dc:title>{esc(book["title"])}</dc:title><dc:language>en</dc:language><dc:creator>Otterly Curious</dc:creator><meta property="dcterms:modified">2026-10-26T00:00:00Z</meta></metadata><manifest>{man}<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/><item id="css" href="style.css" media-type="text/css"/></manifest><spine>' + "".join(f'<itemref idref="{s}"/>' for s in spine) + "</spine></package>")


if __name__ == "__main__":
    build(sys.argv[1])
