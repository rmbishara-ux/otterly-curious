"""lipsync_apply.py E01 : copy finished lip-sync clips (episodes/EXX/lipsync/clips/<shot>.mp4) into ai/ so animate uses them.
Any existing silent hero clip for that shot is moved to ai_silent_backup/ first. Re-run animate+assemble+qa after."""
import json, shutil, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
ep = sys.argv[1]; d = ROOT / "episodes" / ep
plan = json.loads((d / "lipsync" / "plan.json").read_text())
(d / "ai").mkdir(exist_ok=True); (d / "ai_silent_backup").mkdir(exist_ok=True)
done = missing = 0
for p in plan:
    src = d / "lipsync" / "clips" / f"{p['shot']}.mp4"
    if not src.exists() or src.stat().st_size < 10000:
        missing += 1; continue
    dst = d / "ai" / f"{p['shot']}.mp4"
    bak = d / "ai_silent_backup" / f"{p['shot']}.mp4"
    if dst.exists() and not bak.exists() and dst.stat().st_size != src.stat().st_size:
        shutil.move(dst, bak)
    shutil.copy2(src, dst); done += 1
print(f"{ep}: {done} lip-sync clips applied, {missing} still missing")
