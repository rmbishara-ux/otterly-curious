"""voicebatch.py E02 7 : write voice_lines.json (once) and print the next N pending voice requests as a generate_audio_batch body.
voicebatch.py E02 --rec 5,6,7 job1,job2,job3 : record job ids for line idx.   --dl : download resolved urls to audio/<shot>_L<n>.wav"""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pipeline import ledger

ep = sys.argv[1]
d = ROOT / "episodes" / ep
vl, led = d / "voice_lines.json", d / "voice_ledger.json"
if not vl.exists():
    sb = json.loads((d / "storyboard.json").read_text())
    lines, i = [], 0
    for s in sb["shots"]:
        for n, l in enumerate(s["dialogue"], 1):
            lines.append({"idx": i, "shot": s["id"], "line": n, "char": l["char"], "text": l["text"]}); i += 1
    vl.write_text(json.dumps(lines, indent=1))
lines = json.loads(vl.read_text())
cfg = json.loads((ROOT / "bible" / "voice_configs.json").read_text())
if len(sys.argv) > 2 and sys.argv[2] == "--rec":
    for k, j in zip(sys.argv[3].split(","), sys.argv[4].split(",")):
        ledger.add(led, k, job=j)
    print("recorded"); sys.exit()
if len(sys.argv) > 2 and sys.argv[2] == "--dl":
    L = ledger.load(led); (d / "audio").mkdir(exist_ok=True)
    import subprocess
    n = 0
    for l in lines:
        v = L.get(str(l["idx"]), {})
        out = d / "audio" / f"{l['shot']}_L{l['line']}.wav"
        if v.get("url") and not (out.exists() and out.stat().st_size > 1000):
            subprocess.run(["curl", "-sS", "-m", "60", "-o", str(out), v["url"]]); n += 1
    print("downloaded", n, "missing url:", [k for k, v in L.items() if not v.get("url")]); sys.exit()
done = ledger.load(led)
todo = [l for l in lines if str(l["idx"]) not in done][: int(sys.argv[2])]
print(json.dumps([l["idx"] for l in todo]))
out = []
for i, l in enumerate(todo):
    c = cfg[l["char"]]
    out.append({"index": i, "params": {"model": "seed_audio", "prompt": l["text"], "voice_id": c["voice_id"], "voice_type": "preset",
                "pitch_rate": c["settings"]["pitch_rate"], "speech_rate": c["settings"]["speech_rate"]}})
print(json.dumps(out, ensure_ascii=False))
