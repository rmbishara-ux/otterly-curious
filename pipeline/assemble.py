"""Stage 7: ffmpeg assembly -> 1920x1080 30fps H.264 with embedded SRT, plus two 1080x1920 Shorts."""
import subprocess
from pathlib import Path
from .common import ROOT, ep_dir, font_path
from .stages import load_sb, W, H, FPS, ffprobe_dur


def sh(cmd):
    subprocess.run(cmd, check=True)


def srt_time(t):
    ms = int(round(t * 1000))
    return f"{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}"


def timeline(sb):
    t = 0.0
    for s in sb["shots"]:
        s["_t0"] = t
        t += s["duration"]
    return t


def build_srt(sb, shots=None, offset=0.0):
    cues, n = [], 0
    for s in (shots or sb["shots"]):
        for l in s["dialogue"]:
            n += 1
            a = s["_t0"] - offset + l.get("start", 0.5)
            b = a + l.get("length", 2.0)
            who = l["char"].replace("_", " ").title()
            cues.append(f"{n}\n{srt_time(a)} --> {srt_time(b)}\n{who}: {l['text']}\n")
    return "\n".join(cues)


def music_plan(sb):
    """Contiguous runs: theme song over the theme shots, outro song over the outro shots, mood beds elsewhere."""
    runs = []
    for s in sb["shots"]:
        kind = "theme" if "theme" in s["tags"] else "outro" if "outro" in s["tags"] else s["music_mood"]
        if runs and runs[-1]["kind"] == kind:
            runs[-1]["end"] = s["_t0"] + s["duration"]
        else:
            runs.append({"kind": kind, "start": s["_t0"], "end": s["_t0"] + s["duration"]})
    return runs


def build_music(ep, sb, total, out):
    """One continuous music track for the whole episode (no per-shot restarts); shots and Shorts slice from it."""
    mdir = ROOT / "assets" / "music"
    cmd = ["ffmpeg", "-y", "-loglevel", "error"]
    parts, labels = [], []
    for i, r in enumerate(music_plan(sb)):
        f = mdir / f"{r['kind']}.wav"
        if not f.exists():
            f = mdir / "play.wav"
        if not f.exists():
            continue
        ln = r["end"] - r["start"]
        song = r["kind"] in ("theme", "outro")
        vol = 0.85 if song else 0.16
        fin, fout = (0.3, 2.5) if song else (0.8, 1.0)
        ms = int(r["start"] * 1000)
        n = len(labels)
        cmd += ["-stream_loop", "-1", "-i", str(f)]
        parts.append(f"[{n}:a]atrim=0:{ln:.2f},asetpts=PTS-STARTPTS,aresample=44100,aformat=channel_layouts=stereo,volume={vol},"
                     f"afade=t=in:d={fin},afade=t=out:st={max(0.0, ln - fout):.2f}:d={fout},adelay={ms}|{ms}[m{n}]")
        labels.append(f"[m{n}]")
    if not labels:
        return None
    parts.append("".join(labels) + f"amix=inputs={len(labels)}:duration=longest:normalize=0,atrim=0:{total:.2f}[a]")
    cmd += ["-filter_complex", ";".join(parts), "-map", "[a]", "-ac", "2", str(out)]
    sh(cmd)
    return out


def shot_audio(ep, s, out, music_dir, music=None):
    """One WAV per shot: voice lines at their offsets over a quiet mood bed."""
    d = ep_dir(ep)
    cmd = ["ffmpeg", "-y", "-loglevel", "error"]
    parts, labels = [], []
    idx = 0
    if music is not None:
        cmd += ["-ss", f"{s['_t0']:.3f}", "-t", f"{s['duration']:.2f}", "-i", str(music)]
        parts.append(f"[{idx}:a]aresample=44100[bed]")
        labels.append("[bed]")
        idx += 1
    for i, l in enumerate(s["dialogue"]):
        f = ROOT / l["file"] if l.get("file") else None
        if f and f.exists():
            cmd += ["-i", str(f)]
            ms = int(l.get("start", 0.5) * 1000)
            parts.append(f"[{idx}:a]aresample=44100,adelay={ms}|{ms}[v{i}]")
            labels.append(f"[v{i}]")
            idx += 1
    cmd += ["-f", "lavfi", "-t", f"{s['duration']:.2f}", "-i", "anullsrc=r=44100:cl=stereo"]
    parts.append(f"[{idx}:a]aresample=44100[sil]")
    labels.append("[sil]")
    parts.append("".join(labels) + f"amix=inputs={len(labels)}:duration=longest:normalize=0,atrim=0:{s['duration']:.2f},apad=whole_dur={s['duration']:.2f}[a]")
    cmd += ["-filter_complex", ";".join(parts), "-map", "[a]", "-ac", "2", str(out)]
    sh(cmd)


def shot_clip(ep, s, out, big_q=None):
    d = ep_dir(ep)
    src = d / "shots" / f"{s['id']}.mp4"
    vf = f"scale={W}:{H},fps={FPS},format=yuv420p"
    if s.get("text_overlay"):
        txt = s["text_overlay"].replace("'", "’").replace(":", "\\:")
        fs = int(H * 0.075)
        vf += (f",drawtext=fontfile='{font_path()}':text='{txt}':fontcolor=0x1D3557:fontsize={fs}:box=1:boxcolor=0xF4E9D8@0.92:boxborderw={fs//3}"
               f":x=(w-text_w)/2:y=h*0.07:enable='between(t,0.3,{min(s['duration'], 4.5):.2f})'")
    sh(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-vf", vf, "-t", f"{s['duration']:.2f}", "-an", "-c:v", "libx264", "-preset", "veryfast", "-r", str(FPS), str(out)])


def concat(files, out, extra=None):
    lst = Path(str(out) + ".txt")
    lst.write_text("".join(f"file '{Path(f).resolve()}'\n" for f in files))
    sh(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst)] + (extra or ["-c", "copy"]) + [str(out)])
    lst.unlink()


def assemble(ep):
    d = ep_dir(ep)
    sb = load_sb(ep)
    total = timeline(sb)
    tmp = d / "renders" / "tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    vids, auds = [], []
    music = build_music(ep, sb, total, d / "renders" / "music.wav")
    for s in sb["shots"]:
        v, a = tmp / f"{s['id']}.v.mp4", tmp / f"{s['id']}.a.wav"
        shot_clip(ep, s, v)
        shot_audio(ep, s, a, d / "audio", music)
        vids.append(v)
        auds.append(a)
    concat(vids, d / "renders" / "video.mp4")
    concat(auds, d / "renders" / "audio.wav", ["-c", "copy"])
    srt = d / "final" / "captions.srt"
    srt.write_text(build_srt(sb))
    final = d / "renders" / f"{ep}_episode.mp4"
    sh(["ffmpeg", "-y", "-loglevel", "error", "-i", str(d / "renders" / "video.mp4"), "-i", str(d / "renders" / "audio.wav"), "-i", str(srt),
        "-map", "0:v", "-map", "1:a", "-map", "2:s", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-c:s", "mov_text",
        "-metadata:s:s:0", "language=eng", "-movflags", "+faststart", str(final)])
    out = {"episode": str(final), "seconds": total}
    for tag, name in (("short_demo", "short_demo"), ("short_fail", "short_fail")):
        picked = [s for s in sb["shots"] if tag in s["tags"]]
        cap = 29.5 if tag == "short_fail" else 59.5  # voice timing can lengthen shots after tagging
        while len(picked) > 1 and sum(s["duration"] for s in picked) > cap:
            picked.pop(0 if tag == "short_fail" else -1)
        if not picked:
            continue
        vs = [tmp / f"{s['id']}.v.mp4" for s in picked]
        as_ = [tmp / f"{s['id']}.a.wav" for s in picked]
        sv, sa = d / "renders" / f"{name}_v.mp4", d / "renders" / f"{name}_a.wav"
        concat(vs, sv)
        concat(as_, sa, ["-c", "copy"])
        q = sb.get("big_question", "").replace("'", "’").replace(":", "\\:")
        fs = 64
        fc = (f"[0:v]split[a][b];[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30[bg];"
              f"[b]scale=1080:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,"
              f"drawtext=fontfile='{font_path()}':text='{q}':fontcolor=0x1D3557:fontsize={fs}:box=1:boxcolor=0xF4E9D8@0.92:boxborderw=22:x=(w-text_w)/2:y=140:enable='between(t,0,4)',"
              f"format=yuv420p[v]")
        sf = d / "final" / f"{ep}_{name}.mp4"
        sh(["ffmpeg", "-y", "-loglevel", "error", "-i", str(sv), "-i", str(sa), "-filter_complex", fc, "-map", "[v]", "-map", "1:a",
            "-c:v", "libx264", "-preset", "veryfast", "-c:a", "aac", "-r", str(FPS), "-shortest", str(sf)])
        out[name] = str(sf)
        out[name + "_seconds"] = round(sum(s["duration"] for s in picked), 1)
    return out
