"""clipdl.py E03 S002=231332 S018=231333 ... : record Kling clip urls (date from today UTC) in video_ledger.json and download to ai/."""
import json, subprocess, sys, datetime
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
ep = sys.argv[1]
p = ROOT / "episodes" / ep / "video_ledger.json"; d = json.loads(p.read_text())
B = "https://d8j0ntlcm91z4.cloudfront.net/user_3GF0wsWv24c9iFrHaP1guTwfxH4/hf_%s_%s_%s.mp4"
date = __import__("os").environ.get("DATE","20261027")
(ROOT / "episodes" / ep / "ai").mkdir(exist_ok=True)
for a in sys.argv[2:]:
    shot, t = a.split("="); k = f"{ep}-{shot}"
    d[k]["url"] = B % (date, t, d[k]["job"])
    out = ROOT / "episodes" / ep / "ai" / f"{k}.mp4"
    if not out.exists() or out.stat().st_size < 10000:
        subprocess.run(["curl", "-sS", "-m", "180", "-o", str(out), d[k]["url"]])
    print(k, out.stat().st_size)
p.write_text(json.dumps(d, indent=1))
