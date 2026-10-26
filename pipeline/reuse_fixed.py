"""reuse_fixed.py E02 : reuse E01's theme + outro stills and AI clips (identical in every episode); mark them done in the ledger."""
import json, shutil, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pipeline import ledger
ep = sys.argv[1]
def sbl(e): return json.loads((ROOT / "episodes" / e / "storyboard.json").read_text())["shots"]
src = {t: [s for s in sbl("E01") if t in s["tags"]] for t in ("theme", "outro")}
dst = {t: [s for s in sbl(ep) if t in s["tags"]] for t in ("theme", "outro")}
L1 = ledger.load(ROOT / "episodes/E01/image_ledger.json"); V1 = ledger.load(ROOT / "episodes/E01/video_ledger.json")
P = ROOT / "episodes" / ep / "image_ledger.json"; (ROOT / "episodes" / ep / "shots").mkdir(exist_ok=True); (ROOT / "episodes" / ep / "ai").mkdir(exist_ok=True)
VL = ROOT / "episodes" / ep / "video_ledger.json"; n = 0
for t in ("theme", "outro"):
    assert len(src[t]) == len(dst[t]), (t, len(src[t]), len(dst[t]))
    for a, b in zip(src[t], dst[t]):
        shutil.copy(ROOT / "episodes/E01/shots" / f"{a['id']}.png", ROOT / "episodes" / ep / "shots" / f"{b['id']}.png")
        ledger.add(P, b["id"], **L1[a["id"]], reused_from=a["id"])
        ai = ROOT / "episodes/E01/ai" / f"{a['id']}.mp4"
        if ai.exists():
            shutil.copy(ai, ROOT / "episodes" / ep / "ai" / f"{b['id']}.mp4")
            ledger.add(VL, b["id"], **V1[a["id"]], reused_from=a["id"]); n += 1
print(ep, "reused", len(src["theme"]) + len(src["outro"]), "stills,", n, "AI clips")
