"""Stage 2: script.md -> storyboard.json (60-80 shots)."""
import re, sys
from pathlib import Path
from .common import ROOT, ep_dir, write_json
from .script_format import parse, group_shots, words, CHARS

THEME = [  # fixed 30 s theme sequence, 8 shots
    ("driftwood_playground", "morning", {"ollie": "happy"}, "Sunrise over the cove, the sea sparkling. Ollie waves hello.", "wide", 4),
    ("tide_pools", "morning", {"ollie": "excited", "pip": "happy"}, "Ollie and Pip hop between the tide pools.", "follow", 4),
    ("lighthouse_point", "morning", {"gran_mari": "happy"}, "Gran Mari waves from her porch, scarf swinging.", "static", 3),
    ("driftwood_playground", "morning", {"gus": "excited"}, "Gus swoops through, red sneakers kicking up sand.", "pan_right", 3),
    ("kelp_shallows", "morning", {"bean": "happy", "luna": "calm"}, "Bean floats by with Luna glowing softly beside her.", "static", 4),
    ("wonder_shed", "morning", {"ollie": "curious", "pip": "curious"}, "Ollie pulls a shell from his Wonder Pocket and holds it up.", "close", 4),
    ("driftwood_playground", "morning", {"ollie": "happy", "pip": "happy", "gran_mari": "happy", "gus": "happy", "bean": "happy", "luna": "calm"}, "Everyone runs together toward the camera.", "wide", 4),
    ("driftwood_playground", "morning", {"ollie": "excited"}, "Title card: OTTERLY CURIOUS over the sparkling cove.", "static", 4),
]
OUTRO = [
    ("wonder_shed", "golden", {"ollie": "happy", "pip": "happy", "bean": "happy", "gus": "happy", "luna": "calm"}, "Everyone waves goodbye as the sun sets.", "wide", 10),
    ("driftwood_playground", "golden", {"luna": "calm"}, "Soft end card: Luna drifts across the golden cove.", "static", 10),
]
TIME_NAMES = {"golden": "golden_hour"}


def build(ep):
    d = ep_dir(ep)
    meta, beats = parse(d / "script.md")
    shots = []
    n = 0

    def add(**kw):
        nonlocal n
        n += 1
        kw["id"] = f"{ep}-S{n:03d}"
        shots.append(kw)
        return kw

    for b in beats:
        if b["n"] == 2:
            for (loc, tm, chars, act, cam, dur) in THEME:
                add(beat=2, beat_name="Theme song", location=loc, time=TIME_NAMES.get(tm, tm), characters=chars, action=act,
                    camera=cam, dialogue=[], duration=float(dur), music_mood="play", luna_glow=("dim" if "luna" in chars else None),
                    tags=["theme"], text_overlay=None)
            continue
        scene0 = b["scene"]
        for sh in group_shots([i for i in b["items"] if i["type"] != "unparsed"]):
            act = sh["action"]
            opts = act["opts"] if act else {}
            scene = {**scene0, **sh["scene"]}
            chars = {k: v for k, v in opts.items() if k in CHARS}
            for l in sh["lines"]:
                chars.setdefault(l["char"], l["emotion"])
            glow = opts.get("glow")
            if glow:
                chars.setdefault("luna", "calm")
            add(beat=b["n"], beat_name=b["name"], location=scene.get("location"),
                time=TIME_NAMES.get(scene.get("time", "morning"), scene.get("time", "morning")), characters=chars,
                action=(act["text"] if act else ""), camera=opts.get("cam", "static"),
                dialogue=[{"char": l["char"], "emotion": l["emotion"], "text": l["text"]} for l in sh["lines"]],
                duration=0.0, music_mood=scene.get("mood", "play"), luna_glow=glow, tags=[],
                text_overlay=None, continued=bool(sh.get("continued")), _dur=float(opts.get("dur", 4)))
    for (loc, tm, chars, act, cam, dur) in OUTRO:
        add(beat=7, beat_name="Outro", location=loc, time=TIME_NAMES.get(tm, tm), characters=chars, action=act, camera=cam,
            dialogue=[], duration=float(dur), music_mood="cozy", luna_glow="bright" if "luna" in chars else None, tags=["outro"], text_overlay=None)
    # durations: speech-driven for dialogue shots
    for s in shots:
        if s["duration"] == 0.0:
            speech = sum(words(l["text"]) / 2.6 + 0.8 for l in s["dialogue"])
            base = 3.0 if s.get("continued") else s.pop("_dur", 4.0)
            s["duration"] = round(max(base, speech + 1.0), 2)
        s.pop("_dur", None)
        s.pop("continued", None)
        s["book_safe"] = s["camera"] in ("wide", "static", "pan_right", "pan_up", "slow_push", "follow", "tilt_up")
    # on-screen Big Question in the first shot that contains it (beat 1)
    bq = meta.get("big_question", "").lower()
    for s in shots:
        if s["beat"] == 1 and any(bq and bq in l["text"].lower() for l in s["dialogue"]):
            s["text_overlay"] = meta["big_question"]
            break
    # shorts tags
    fail = [s for s in shots if s["beat"] == 4]
    acc, picked = 0.0, []
    for s in fail:
        if acc + s["duration"] > 30:
            break
        picked.append(s)
        acc += s["duration"]
    for s in picked:
        s["tags"].append("short_fail")
    b5 = [s for s in shots if s["beat"] == 5]
    start = next((i for i, s in enumerate(b5) if s["camera"] in ("top_down", "timelapse") or s["duration"] >= 6), 0)
    cand = b5[max(0, start - 1):]
    acc, picked = 0.0, []
    for s in reversed(cand):
        if acc + s["duration"] > 60:
            break
        picked.insert(0, s)
        acc += s["duration"]
    for s in picked:
        s["tags"].append("short_demo")
    total = sum(s["duration"] for s in shots)
    sb = {"episode": ep, "title": meta.get("title"), "big_question": meta.get("big_question"), "value": meta.get("value"),
          "shot_count": len(shots), "total_seconds": round(total, 1), "shots": shots}
    write_json(d / "storyboard.json", sb)
    return sb


if __name__ == "__main__":
    for ep in sys.argv[1:]:
        sb = build(ep)
        print(ep, sb["shot_count"], "shots", round(sb["total_seconds"] / 60, 2), "min")
