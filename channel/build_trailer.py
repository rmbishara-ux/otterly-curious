"""Channel trailer (about 44 s) cut from approved episode footage + 2 new Ollie lines. Run: python3 channel/build_trailer.py"""
import subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pipeline.common import font_path
W, H, FPS = 1920, 1080, 30
T = ROOT / "channel" / "trailer"; (T / "tmp").mkdir(exist_ok=True)
A = lambda ep, s: ROOT / "episodes" / ep / "ai" / f"{ep}-{s}.mp4"
# (clip, seconds, overlay text or None, sub text)
SEGS = [
    (A("E01", "S006"), 4.5, None, None),
    (A("E01", "S007"), 3.0, None, None),
    (A("E01", "S009"), 3.0, None, None),
    (A("E01", "S010"), 3.0, None, None),
    (A("E01", "S003"), 4.5, "Why does the water go away?", None),
    (A("E02", "S002"), 4.5, "Why do otters hold hands?", None),
    (A("E03", "S002"), 4.5, "Where does a rainbow come from?", None),
    (A("E03", "S037"), 6.0, None, None),
    (A("E01", "S012"), 5.0, None, None),
    (A("E01", "S064"), 6.0, "Otterly Curious", "A new big question every Saturday"),
]
def esc(t): return t.replace("'", "’").replace(":", "\\:")
files, t0, starts = [], 0.0, []
for i, (clip, dur, txt, sub) in enumerate(SEGS):
    out = T / "tmp" / f"seg{i}.mp4"
    vf = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},tpad=stop_mode=clone:stop_duration={dur:.2f}"
    if txt:
        big = txt == "Otterly Curious"
        fs = 120 if big else 78
        y = "h*0.12" if big else "h*0.07"
        vf += (f",drawtext=fontfile='{font_path()}':text='{esc(txt)}':fontcolor=0x1D3557:fontsize={fs}:box=1:boxcolor=0xF4E9D8@0.92:boxborderw={fs//3}"
               f":x=(w-text_w)/2:y={y}:enable='between(t,0.3,{dur-0.2:.2f})'")
    if sub:
        vf += (f",drawtext=fontfile='{font_path()}':text='{esc(sub)}':fontcolor=0xFFFFFF:fontsize=60:box=1:boxcolor=0x1D3557@0.85:boxborderw=18"
               f":x=(w-text_w)/2:y=h*0.30:enable='between(t,0.8,{dur-0.2:.2f})'")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(clip), "-vf", vf + ",format=yuv420p", "-t", f"{dur:.2f}", "-an", "-c:v", "libx264", "-preset", "veryfast", str(out)], check=True)
    files.append(out); starts.append(t0); t0 += dur
total = t0
lst = T / "tmp" / "list.txt"; lst.write_text("".join(f"file '{f}'\n" for f in files))
vid = T / "tmp" / "video.mp4"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(vid)], check=True)
# audio: instrumental bed + three Ollie lines
voices = [(T / "v_hi.wav", 0.9), (T / "v_week.wav", starts[7] + 0.5), (T / "v_find.wav", starts[8] + 1.2)]
cmd = ["ffmpeg", "-y", "-loglevel", "error", "-stream_loop", "-1", "-i", str(ROOT / "assets/music/play.wav")]
fc = [f"[0:a]atrim=0:{total:.2f},asetpts=PTS-STARTPTS,aresample=44100,aformat=channel_layouts=stereo,volume=0.42,afade=t=in:d=0.5,afade=t=out:st={total-3:.2f}:d=3[bed]"]
labs = ["[bed]"]
for i, (f, at) in enumerate(voices, 1):
    cmd += ["-i", str(f)]; ms = int(at * 1000)
    fc.append(f"[{i}:a]aresample=44100,aformat=channel_layouts=stereo,adelay={ms}|{ms}[v{i}]"); labs.append(f"[v{i}]")
fc.append("".join(labs) + f"amix=inputs={len(labs)}:duration=longest:normalize=0,atrim=0:{total:.2f}[a]")
aud = T / "tmp" / "audio.wav"
subprocess.run(cmd + ["-filter_complex", ";".join(fc), "-map", "[a]", "-ac", "2", str(aud)], check=True)
final = T / "Otterly_Curious_channel_trailer.mp4"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(vid), "-i", str(aud), "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(final)], check=True)
print(final, round(total, 1), "s")
