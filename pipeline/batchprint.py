"""Print the next N pending image requests as a generate_image_batch body (for hand-fulfilled runs)."""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
ep, n = sys.argv[1], int(sys.argv[2])
reqs = json.loads((ROOT / "episodes" / ep / "image_requests.json").read_text())
done = json.loads((ROOT / "episodes" / ep / "image_ledger.json").read_text()) if (ROOT / "episodes" / ep / "image_ledger.json").exists() else {}
todo = [r for r in reqs if r["id"] not in done][:n]
print(json.dumps([r["id"] for r in todo]))
print(json.dumps([{"index": i, "params": {"model": "nano_banana_pro", "aspect_ratio": "16:9", "resolution": "2k",
      "prompt": r["prompt"].replace(" . ", " ").replace("  ", " "), "medias": [{"value": j, "role": "image_references"} for j in r["refs"]]}} for i, r in enumerate(todo)], ensure_ascii=False))
