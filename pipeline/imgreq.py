"""imgreq.py E02 : write image_requests.json from the storyboard (one request per unique still)."""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pipeline.prompts import compact_request
ep = sys.argv[1]
sb = json.loads((ROOT / "episodes" / ep / "storyboard.json").read_text())
reqs = []
for s in sb["shots"]:
    if s.get("still_of"):
        continue
    r = compact_request(s)
    reqs.append({"id": s["id"], "prompt": r["prompt"], "refs": r["refs"], "seed": r["seed"]})
(ROOT / "episodes" / ep / "image_requests.json").write_text(json.dumps(reqs, indent=1))
print(ep, len(reqs), "requests")
