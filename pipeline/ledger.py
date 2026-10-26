"""Tiny ledger helper for hand-fulfilled (manifest) generations: records job ids/urls and downloads them."""
import json, sys, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent

def load(p):
    p = Path(p)
    return json.loads(p.read_text()) if p.exists() else {}

def save(p, d):
    Path(p).write_text(json.dumps(d, indent=1))

def add(p, key, **kw):
    d = load(p); d.setdefault(str(key), {}).update(kw); save(p, d)

def download(ledger, outdir, ext, pattern="{key}", only=None):
    d = load(ledger); Path(outdir).mkdir(parents=True, exist_ok=True); n = 0
    for k, v in d.items():
        if only and k not in only: continue
        u = v.get("url")
        if not u: continue
        out = Path(outdir) / (pattern.format(key=k, **v) + ext)
        if out.exists() and out.stat().st_size > 1000: continue
        r = subprocess.run(["curl", "-sS", "-m", "90", "-o", str(out), u], capture_output=True, text=True)
        if r.returncode: print("FAIL", k, r.stderr[:80])
        else: n += 1
    print("downloaded", n)


def resolve(ledger, hint_hms, window=(-3, 20), ext=".wav", date="20261026", only=None):
    """CDN file names are hf_<date>_<hhmmss>_<jobid><ext>; the time is near submission. Probe a small window per job."""
    import datetime as dt
    base = dt.datetime.strptime(date + hint_hms, "%Y%m%d%H%M%S")
    B = "https://d8j0ntlcm91z4.cloudfront.net/user_3GF0wsWv24c9iFrHaP1guTwfxH4/"
    d = load(ledger); found = 0
    for k, v in d.items():
        if v.get("url") or (only and k not in only) or not v.get("job"): continue
        for off in range(window[0], window[1] + 1):
            t = (base + dt.timedelta(seconds=off)).strftime("%Y%m%d_%H%M%S")
            u = f"{B}hf_{t}_{v['job']}{ext}"
            r = subprocess.run(["curl", "-sS", "-I", "-m", "15", "-o", "/dev/null", "-w", "%{http_code}", u], capture_output=True, text=True)
            if r.stdout.strip() == "200":
                v["url"] = u; found += 1; break
    save(ledger, d)
    print("resolved", found, "of", len([1 for v in d.values() if v.get('job')]))


def sheet(paths, out, cols=4, w=480, labels=None):
    """Contact sheet for fast visual QA of many stills in one image."""
    from PIL import Image, ImageDraw
    ims = [Image.open(p).convert("RGB").resize((w, int(w * 9 / 16))) for p in paths]
    rows = (len(ims) + cols - 1) // cols
    h = ims[0].height
    S = Image.new("RGB", (cols * w, rows * h), (255, 255, 255))
    for i, im in enumerate(ims):
        S.paste(im, ((i % cols) * w, (i // cols) * h))
        if labels:
            ImageDraw.Draw(S).text(((i % cols) * w + 6, (i // cols) * h + 4), labels[i], fill=(255, 0, 0))
    S.save(out)
