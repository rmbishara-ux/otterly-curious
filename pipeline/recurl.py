"""recurl.py E05 voice 0=JOB@HHMMSS ... : record job id + exact url (date 20261027 default, ext wav) in voice_ledger.json.
recurl.py E05 image E05-S013=JOB@HHMMSS ... : same for image_ledger.json (ext png). Use DATE=YYYYMMDD env to override."""
import json, os, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pipeline import ledger
ep, kind = sys.argv[1], sys.argv[2]
date = os.environ.get("DATE", "20261027")
B = "https://d8j0ntlcm91z4.cloudfront.net/user_3GF0wsWv24c9iFrHaP1guTwfxH4/hf_%s_%s_%s.%s"
P = ROOT / "episodes" / ep / ("voice_ledger.json" if kind == "voice" else "image_ledger.json")
ext = "wav" if kind == "voice" else "png"
for a in sys.argv[3:]:
    k, rest = a.split("=")
    job, ts = rest.split("@")
    kw = dict(job=job, url=B % (date, ts, job, ext))
    if kind == "image": kw.update(attempt=1, cost=2)
    ledger.add(P, k, **kw)
print("recorded", len(sys.argv) - 3)
