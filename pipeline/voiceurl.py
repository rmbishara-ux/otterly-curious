"""voiceurl.py E04 0=013712 1=013712 ... [D=20261027] : write exact result URLs (from jobs_wait) into voice_ledger.json."""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
ep = sys.argv[1]; p = ROOT / "episodes" / ep / "voice_ledger.json"; L = json.loads(p.read_text())
date = "20261027"
B = "https://d8j0ntlcm91z4.cloudfront.net/user_3GF0wsWv24c9iFrHaP1guTwfxH4/hf_%s_%s_%s.wav"
for a in sys.argv[2:]:
    k, v = a.split("=")
    if k == "D": date = v; continue
    import datetime, subprocess
    base = datetime.datetime.strptime(date + v, "%Y%m%d%H%M%S")
    for off in sorted(range(-10, 41), key=lambda o: (abs(o - 12), o)):  # guess is submit time; completion lands ~0-40 s later
        t = (base + datetime.timedelta(seconds=off)).strftime("%H%M%S")
        u = B % (date, t, L[k]["job"])
        if subprocess.run(["curl", "-sS", "-I", "-m", "15", "-o", "/dev/null", "-w", "%{http_code}", u], capture_output=True, text=True).stdout.strip() == "200":
            L[k]["url"] = u; break
p.write_text(json.dumps(L, indent=1)); print("urls set; missing:", [k for k, v in L.items() if not v.get("url")])
