"""Stage 8: automated QA. The episode does not move to final/ until every check passes."""
import re, shutil, subprocess
from pathlib import Path
import numpy as np
from PIL import Image
from .common import ROOT, ep_dir, read_json, write_json
from .stages import load_sb, ffprobe_dur

# Approximate signature colors (RGB) per character, used as a cheap on-model presence check (see consistency note in docs).
KEY = {"ollie": [(217, 164, 65)], "pip": [(124, 184, 234), (233, 139, 90)], "gran_mari": [(233, 136, 115)],
       "gus": [(216, 58, 58)], "bean": [(183, 154, 224)], "luna": [(205, 189, 235)]}
MIN_FRAC = {"ollie": 0.0006, "pip": 0.0004, "gran_mari": 0.0004, "gus": 0.0002, "bean": 0.0002, "luna": 0.0004}


def color_frac(img, rgb, tol=38):
    a = np.asarray(img.convert("RGB").resize((480, 270)), dtype=np.int16)
    d = np.abs(a - np.array(rgb, dtype=np.int16)).sum(axis=2)
    return float((d < tol * 1.7).mean())


def drift_check(ep, sb):
    """Flags shots where a character who should be present shows none of their signature colors. A cheap proxy for
    drift; a face-embedding model is the next upgrade. Writes logs/EXX_drift.json."""
    flags = []
    d = ep_dir(ep)
    for s in sb["shots"]:
        p = d / "shots" / f"{s['id']}.png"
        if not p.exists():
            flags.append({"shot": s["id"], "issue": "missing still"})
            continue
        im = Image.open(p)
        for c in s["characters"]:
            best = max(color_frac(im, k) for k in KEY[c])
            if best < MIN_FRAC[c]:
                flags.append({"shot": s["id"], "char": c, "issue": f"signature color not found ({best:.5f})"})
    write_json(ROOT / "logs" / f"{ep}_drift.json", flags)
    return flags


def style_check(ep, sb, sample=12):
    """Kid-safe look: not too dark, not mostly black. Samples evenly across the episode."""
    d = ep_dir(ep)
    shots = sb["shots"][:: max(1, len(sb["shots"]) // sample)]
    bad = []
    for s in shots:
        p = d / "shots" / f"{s['id']}.png"
        if not p.exists():
            continue
        g = np.asarray(Image.open(p).convert("L").resize((240, 135)), dtype=np.float32) / 255
        if g.mean() < 0.25 or (g < 0.08).mean() > 0.15:
            bad.append(s["id"])
    return bad


def audible(path):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(path), "-af", "volumedetect", "-f", "null", "-"], capture_output=True, text=True)
    m = re.search(r"mean_volume:\s*(-?[\d.]+) dB", r.stderr)
    return float(m.group(1)) if m else -99.0


def parse_srt(p):
    cues = []
    for blk in Path(p).read_text().strip().split("\n\n"):
        lines = blk.splitlines()
        m = re.match(r"(\d+):(\d+):(\d+),(\d+) --> (\d+):(\d+):(\d+),(\d+)", lines[1])
        v = list(map(int, m.groups()))
        cues.append((v[0] * 3600 + v[1] * 60 + v[2] + v[3] / 1000, v[4] * 3600 + v[5] * 60 + v[6] + v[7] / 1000))
    return cues


def run_qa(ep, assembled):
    d = ep_dir(ep)
    sb = load_sb(ep)
    checks = []

    def chk(name, ok, detail=""):
        checks.append({"check": name, "pass": bool(ok), "detail": detail})

    dur = ffprobe_dur(assembled["episode"])
    chk("runtime 6:00-8:00", 360 <= dur <= 480, f"{dur/60:.2f} min")
    n_lines = sum(len(s["dialogue"]) for s in sb["shots"])
    quiet = []
    for s in sb["shots"]:
        for l in s["dialogue"]:
            f = ROOT / l["file"] if l.get("file") else None
            if not f or not f.exists() or audible(f) < -45:
                quiet.append(f"{s['id']}:{l['char']}")
    chk("every line audible", not quiet, f"{n_lines} lines, problems: {quiet[:5]}")
    nomotion = [s["id"] for s in sb["shots"] if not (d / "shots" / f"{s['id']}.mp4").exists()]
    long_ = [s["id"] for s in sb["shots"] if s["duration"] > 8]
    chk("no shot >8s without motion", not nomotion, f"missing clips: {nomotion[:5]}; shots >8s (all have motion): {long_}")
    cues = parse_srt(d / "final" / "captions.srt")
    ordered = all(cues[i][1] <= cues[i + 1][0] + 0.01 for i in range(len(cues) - 1)) and all(0 <= a < b <= dur + 0.5 for a, b in cues)
    chk("captions in sync", ordered and len(cues) == n_lines, f"{len(cues)} cues vs {n_lines} lines")
    flags = drift_check(ep, sb)
    chk("no character drift flags open", not flags, f"{len(flags)} flags")
    bad = style_check(ep, sb)
    chk("style/brightness on sampled frames", not bad, f"dark frames: {bad}")
    sd, sf = assembled.get("short_demo_seconds", 0), assembled.get("short_fail_seconds", 0)
    chk("Short (demo) 45-60 s", 45 <= sd <= 60, f"{sd}s")
    chk("Short (fail) 20-30 s", 20 <= sf <= 30, f"{sf}s")
    passed = all(c["pass"] for c in checks)
    rep = {"episode": ep, "passed": passed, "checks": checks}
    write_json(d / "qa_report.json", rep)
    md = [f"# QA report {ep}: {'PASS' if passed else 'FAIL'}", ""] + [f"- {'PASS' if c['pass'] else 'FAIL'} | {c['check']} | {c['detail']}" for c in checks]
    (d / "qa_report.md").write_text("\n".join(md) + "\n")
    if passed:
        shutil.copy(assembled["episode"], d / "final" / Path(assembled["episode"]).name)
    return rep
