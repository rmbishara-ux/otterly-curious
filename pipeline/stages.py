"""Stages 3-6: images, animation, voice, music. Each is cached and cost-logged; adapters may queue work (Pending)."""
import json, os, subprocess
from pathlib import Path
from . import adapters
from .adapters.base import Pending, Unavailable
from .common import ROOT, ep_dir, read_json, write_json, Cache, CostLog, stable_seed
from .prompts import shot_prompt, motion_prompt

DRAFT = os.environ.get("QUALITY", "final") == "draft"
W, H, FPS = (960, 540, 15) if DRAFT else (1920, 1080, 30)


def sb_path(ep):
    return ep_dir(ep) / "storyboard.json"


def load_sb(ep):
    return read_json(sb_path(ep))


def ffprobe_dur(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)], capture_output=True, text=True)
    return float(r.stdout.strip() or 0)


def still_id(s):
    return s.get("still_of", s["id"])


def split_long(ep, max_len=11.0):
    """Cut long multi-line dialogue shots into cut-ins that reuse the parent still (no extra image cost)."""
    sb = load_sb(ep)
    out, n_split = [], 0
    for s in sb["shots"]:
        if s["duration"] <= max_len or len(s["dialogue"]) < 2 or s.get("still_of"):
            out.append(s)
            continue
        groups, cur, t = [], [], 0.5
        for l in s["dialogue"]:
            ln = l.get("length", 2.0) + 0.4
            if cur and t + ln > max_len:
                groups.append(cur)
                cur, t = [], 0.5
            cur.append(l)
            t += ln
        groups.append(cur)
        if len(groups) < 2:
            out.append(s)
            continue
        n_split += 1
        for gi, g in enumerate(groups):
            t = 0.5
            for l in g:
                l["start"] = round(t, 2)
                t += l.get("length", 2.0) + 0.4
            ns = dict(s)
            ns["dialogue"] = g
            ns["duration"] = round(t + 0.6, 2)
            ns["tags"] = list(s["tags"])
            if gi:
                ns["id"] = s["id"] + chr(ord("a") + gi)
                ns["still_of"] = s["id"]
                ns["camera"] = "close" if s["camera"] != "close" else "slow_push"
                ns["action"] = s["action"]
                ns["text_overlay"] = None
            out.append(ns)
    sb["shots"] = out
    sb["shot_count"] = len(out)
    sb["total_seconds"] = round(sum(x["duration"] for x in out), 1)
    write_json(sb_path(ep), sb)
    print(f"split_long: {n_split} shots split -> {len(out)} shots, {sb['total_seconds']}s")


def run_images(ep):
    d, sb, cache, log, ad = ep_dir(ep), load_sb(ep), None, CostLog(ep), adapters.get("image", ep)
    cache = Cache(ep)
    pending = 0
    for s in sb["shots"]:
        if s.get("still_of"):
            continue
        out = d / "shots" / f"{s['id']}.png"
        req = shot_prompt(s)
        if cache.hit(f"img:{s['id']}", req, out):
            continue
        log.check_budget()
        try:
            cost = ad.generate(req, out)
        except Pending:
            pending += 1
            continue
        log.log("image", ad.name, req["prompt"], req["seed"], cost, out, ad.unit)
        cache.put(f"img:{s['id']}", req)
    print(f"images: {len(sb['shots']) - pending} ready, {pending} queued")
    return pending


def kenburns(still, out, dur, camera):
    frames = max(1, int(round(dur * FPS)))
    z = {"slow_push": "min(zoom+0.0007,1.12)", "close": "min(zoom+0.0010,1.18)", "wide": "if(eq(on,1),1.12,max(zoom-0.0006,1.0))"}.get(camera, "min(zoom+0.0005,1.08)")
    x = {"pan_right": f"(iw-iw/zoom)*on/{frames}", "follow": f"(iw-iw/zoom)*on/{frames}"}.get(camera, "iw/2-(iw/zoom/2)")
    vf = f"scale={W*2}:-2,zoompan=z='{z}':x='{x}':y='ih/2-(ih/zoom/2)':d={frames}:s={W}x{H}:fps={FPS},format=yuv420p"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(still), "-vf", vf, "-t", f"{dur:.2f}", "-c:v", "libx264", "-preset", "veryfast", str(out)], check=True)


def run_animate(ep):
    d, sb, cache, log, ad = ep_dir(ep), load_sb(ep), Cache(ep), CostLog(ep), None
    ad = adapters.get("video", ep)
    n_ai = n_kb = pending = 0
    for s in sb["shots"]:
        still, out = d / "shots" / f"{still_id(s)}.png", d / "shots" / f"{s['id']}.mp4"
        if not still.exists():
            continue
        req = {"image": str(still), "motion": motion_prompt(s), "seconds": s["duration"], "seed": stable_seed(s["id"], "vid")}
        if cache.hit(f"vid:{s['id']}", req, out):
            continue
        try:
            cost = ad.generate(req, out)
            log.log("video", ad.name, req["motion"], req["seed"], cost, out, ad.unit)
            n_ai += 1
        except Pending:
            pending += 1
            kenburns(still, out, s["duration"], s["camera"])  # keep a usable clip while the AI clip is queued
            n_kb += 1
            continue
        except Unavailable:
            kenburns(still, out, s["duration"], s["camera"])
            n_kb += 1
        cache.put(f"vid:{s['id']}", req)
    print(f"animate: {n_ai} AI clips, {n_kb} Ken Burns fallbacks, {pending} AI clips queued")


def run_voice(ep):
    """Generate each line with the fixed per-character voice, measure it, and feed durations back to the storyboard."""
    d, sb, cache, log, ad = ep_dir(ep), load_sb(ep), Cache(ep), CostLog(ep), adapters.get("voice", ep)
    pending = 0
    for s in sb["shots"]:
        t = 0.5
        for i, l in enumerate(s["dialogue"]):
            ext = "mp3" if ad.name == "elevenlabs" else "wav"
            out = d / "audio" / f"{s['id']}_L{i+1}.{ext}"
            req = {"char": l["char"], "emotion": l["emotion"], "text": l["text"]}
            if not cache.hit(f"voice:{s['id']}:{i}", req, out):
                try:
                    cost = ad.generate(req, out)
                except Pending:
                    pending += 1
                    l["start"], l["length"] = round(t, 2), round(len(l["text"].split()) / 2.6 + 0.3, 2)
                    t += l["length"] + 0.4
                    continue
                log.log("voice", ad.name, l["text"], 0, cost, out, ad.unit)
                cache.put(f"voice:{s['id']}:{i}", req)
            l["file"] = str(out.relative_to(ROOT))
            l["length"] = round(ffprobe_dur(out), 2)
            l["start"] = round(t, 2)
            t += l["length"] + 0.4
        if s["dialogue"]:
            s["duration"] = round(max(s["duration"], t + 0.6), 2)
    sb["total_seconds"] = round(sum(s["duration"] for s in sb["shots"]), 1)
    write_json(sb_path(ep), sb)
    print(f"voice: done, {pending} queued, total {sb['total_seconds']}s")


def run_music(ep):
    d, sb, cache, log, ad = ep_dir(ep), load_sb(ep), Cache(ep), CostLog(ep), adapters.get("music", ep)
    moods = sorted({s["music_mood"] for s in sb["shots"]} | {"theme", "outro"})
    songs = (ROOT / "bible" / "songs.md").read_text()
    pending = 0
    for m in moods:
        out = d / "audio" / f"bed_{m}.wav"
        shared = ROOT / "assets" / "music" / f"{m}.wav"
        if shared.exists():
            continue
        req = {"mood": m, "seconds": 30 if m == "theme" else 20 if m == "outro" else 60, "prompt_source": "bible/songs.md" if m in ("theme", "outro") else f"instrumental {m} loop, ukulele, glockenspiel, soft claps",
               "lyrics_doc": songs[:0]}
        if cache.hit(f"music:{m}", req, out):
            continue
        try:
            cost = ad.generate(req, out)
        except Pending:
            pending += 1
            continue
        log.log("music", ad.name, str(req["prompt_source"]), 0, cost, out, ad.unit)
        cache.put(f"music:{m}", req)
    print(f"music: {len(moods) - pending} ready, {pending} queued")
