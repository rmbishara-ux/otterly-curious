"""lipsync_prep.py EXX : restore stills/voices/clips from the CDN ledgers, then write one voice track per dialogue shot
(episodes/EXX/lipsync/tracks/<shot>.mp3, voices at their storyboard offsets) and lipsync/plan.json for Wan 2.7 lip-sync."""
import json, math, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(ROOT)); os.chdir(ROOT)
from pipeline.assemble import load_sb, timeline
from pipeline.stages import still_id
ep = sys.argv[1]; E = f"episodes/{ep}"
for d in ("shots", "audio", "ai", "lipsync/tracks"): os.makedirs(f"{E}/{d}", exist_ok=True)
jobs = [(v["url"], f"{E}/shots/{k}.png") for k, v in json.load(open(f"{E}/image_ledger.json")).items() if v.get("url")]
vl, vled = json.load(open(f"{E}/voice_lines.json")), json.load(open(f"{E}/voice_ledger.json"))
jobs += [(vled[str(v["idx"])]["url"], f"{E}/audio/{v['shot']}_L{v['line']}.wav") for v in vl if vled.get(str(v["idx"]), {}).get("url")]
jobs += [(v["url"], f"{E}/ai/{k}.mp4") for k, v in json.load(open(f"{E}/video_ledger.json")).items() if v.get("url")]
def get(j):
    u, p = j
    return 0 if os.path.exists(p) and os.path.getsize(p) > 1000 else subprocess.run(["curl", "-sS", "-f", "-m", "180", "-o", p, u]).returncode
with ThreadPoolExecutor(16) as ex: rc = list(ex.map(get, jobs))
print(f"restored {len(jobs)} files, {sum(1 for r in rc if r)} failures")
sb = load_sb(ep); timeline(sb); il = json.load(open(f"{E}/image_ledger.json")); plan = []
for s in sb["shots"]:
    if not s["dialogue"]: continue
    gen = min(15, max(2, math.ceil(s["duration"]))); cmd = ["ffmpeg", "-y", "-loglevel", "error"]; parts, labs = [], []
    for i, l in enumerate(s["dialogue"]):
        cmd += ["-i", l["file"]]; ms = int(l.get("start", 0.5) * 1000)
        parts.append(f"[{i}:a]aresample=44100,adelay={ms}|{ms}[v{i}]"); labs.append(f"[v{i}]")
    n = len(s["dialogue"]); cmd += ["-f", "lavfi", "-t", str(gen), "-i", "anullsrc=r=44100:cl=stereo"]; labs.append(f"[{n}:a]")
    parts.append("".join(labs) + f"amix=inputs={len(labs)}:duration=longest:normalize=0,atrim=0:{gen},apad=whole_dur={gen}[a]")
    subprocess.run(cmd + ["-filter_complex", ";".join(parts), "-map", "[a]", "-ac", "2", "-b:a", "160k", f"{E}/lipsync/tracks/{s['id']}.mp3"], check=True)
    st = still_id(s)
    plan.append(dict(shot=s["id"], still=st, img_job=il[st]["job"], dur=round(s["duration"], 2), gen=gen, camera=s.get("camera"),
                     chars=list((s.get("characters") or {}).keys()),
                     lines=[dict(char=l["char"], text=l["text"], start=l.get("start", 0.5), length=l.get("length")) for l in s["dialogue"]]))
json.dump(plan, open(f"{E}/lipsync/plan.json", "w"), indent=1)
print(f"{ep}: {len(plan)} dialogue shots, {sum(p['gen'] for p in plan)} s to generate, over 15 s: {[p['shot'] for p in plan if p['dur'] > 15]}")
