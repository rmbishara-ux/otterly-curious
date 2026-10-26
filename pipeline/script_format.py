"""Parse and lint Otterly Curious episode scripts (episodes/EXX/script.md).

Format
------
# E01: Title
big_question: ...
value: ...
demo: ...
book_title: ...
bean_word: ...

## BEAT 1 | Cold open | 0:00-0:15 | location=driftwood_playground | time=morning | mood=play
> Action text {ollie=happy, pip=worried; glow=bright; cam=slow_push; dur=6}
OLLIE (curious): Why does the water go away?
SCENE: location=tide_pools | time=morning | mood=wonder     (switch location inside a beat)
"""
import re, sys, json
from pathlib import Path

CHARS = {"ollie", "pip", "gran_mari", "gus", "bean", "luna"}
KID_LIMIT = {"ollie", "pip", "gus", "bean"}
LOCATIONS = {"kelp_shallows", "tide_pools", "lighthouse_point", "driftwood_playground", "wonder_shed"}
EMOTIONS = {"happy", "curious", "worried", "surprised", "sorry", "proud", "neutral", "excited", "sleepy", "determined", "calm", "playful"}
GLOW = {"dim", "bright", "sparkle"}
BANNED = ["human", "mom", "dad", "mother", "father", "woman", "man ", "screen", "phone", "tablet", "tv ", "youtube",
          "buy", "brand", "candy", "scared", "kill", "die ", "stupid", "shut up"]
HDR = re.compile(r"^##\s*BEAT\s*(\d)\s*\|\s*([^|]+)\|\s*([^|]+)\|?(.*)$")
DLG = re.compile(r"^([A-Z_]+)\s*\(([a-z]+)\)\s*:\s*(.+)$")
ACT = re.compile(r"^>\s*(.*?)(?:\{(.*)\})?\s*$")


def kv(s):
    out = {}
    for part in re.split(r"[|;,]", s or ""):
        if "=" in part:
            k, v = part.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def parse(path):
    text = Path(path).read_text()
    meta, beats, cur, scene = {}, [], None, {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("# "):
            meta["title"] = line[2:].strip()
            continue
        m = HDR.match(line)
        if m:
            scene = kv(m.group(4))
            cur = {"n": int(m.group(1)), "name": m.group(2).strip(), "range": m.group(3).strip(), "items": [], "scene": dict(scene)}
            beats.append(cur)
            continue
        if cur is None:
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
            continue
        if line.startswith("SCENE:"):
            scene = {**scene, **kv(line[6:])}
            continue
        d = DLG.match(line)
        if d:
            cur["items"].append({"type": "line", "char": d.group(1).lower(), "emotion": d.group(2),
                                 "text": d.group(3).strip().strip('"'), "scene": dict(scene)})
            continue
        a = ACT.match(line)
        if a and line.startswith(">"):
            opts = kv(a.group(2))
            cur["items"].append({"type": "action", "text": a.group(1).strip(), "opts": opts, "scene": dict(scene)})
            continue
        cur["items"].append({"type": "unparsed", "text": line})
    return meta, beats


def words(s):
    return len(re.findall(r"[A-Za-z']+", s))


def sentences(s):
    return [x for x in re.split(r"(?<=[.!?])\s+", s) if x.strip()]


MAX_LINES_PER_SHOT = 3


def group_shots(items):
    """Group beat items into shots: an action opens a shot; up to 3 following lines share it.
    Lines with no preceding action open their own shot, inheriting the previous shot's staging."""
    shots, cur = [], None
    for it in items:
        if it["type"] == "action":
            cur = {"action": it, "lines": [], "scene": it["scene"]}
            shots.append(cur)
        elif it["type"] == "line":
            if cur is None or len(cur["lines"]) >= MAX_LINES_PER_SHOT:
                prev = cur
                cur = {"action": prev["action"] if prev else None, "lines": [], "scene": it["scene"], "continued": True}
                shots.append(cur)
            cur["lines"].append(it)
    return shots


def shot_seconds(shot):
    speech = sum(words(l["text"]) / 2.6 + 0.8 for l in shot["lines"])
    base = float(shot["action"]["opts"].get("dur", 4)) if (shot["action"] and not shot.get("continued")) else 3.0
    return max(base, speech + 1.0)


def est_seconds(item):
    if item["type"] == "line":
        return max(5.0, words(item["text"]) / 2.6 + 1.5)
    return float(item["opts"].get("dur", 6))


def lint(path):
    meta, beats = parse(path)
    errs, warns = [], []
    for k in ("big_question", "value", "demo", "book_title", "bean_word"):
        if not meta.get(k):
            errs.append(f"missing meta: {k}")
    if meta.get("big_question") and not meta["big_question"].endswith("?"):
        errs.append("big_question must end with ?")
    nums = [b["n"] for b in beats]
    if nums != [1, 2, 3, 4, 5, 6, 7]:
        errs.append(f"beats must be 1..7 in order, got {nums}")
    shots, secs = 0, 0.0
    bean_lines = []
    glows = 0
    first_kid_q = False
    for b in beats:
        if b["n"] == 2:
            continue  # fixed theme sequence, injected by the storyboard stage
        if b["scene"].get("location") and b["scene"]["location"] not in LOCATIONS:
            errs.append(f"beat {b['n']}: unknown location {b['scene']['location']}")
        for it in b["items"]:
            if it["type"] == "unparsed":
                errs.append(f"beat {b['n']}: unparsed line: {it['text'][:50]}")
                continue
            loc = it["scene"].get("location")
            if b["n"] != 2 and loc and loc not in LOCATIONS:
                errs.append(f"beat {b['n']}: unknown location {loc}")
            low = it["text"].lower() + " "
            for w in BANNED:
                if w in low:
                    errs.append(f"beat {b['n']}: banned word '{w.strip()}' in: {it['text'][:50]}")
            if it["type"] == "line":
                c = it["char"]
                if c not in CHARS - {"luna"}:
                    errs.append(f"beat {b['n']}: bad speaker {c}")
                if it["emotion"] not in EMOTIONS:
                    errs.append(f"beat {b['n']}: bad emotion {it['emotion']} for {c}")
                if c in KID_LIMIT:
                    for s in sentences(it["text"]):
                        if words(s) > 12:
                            errs.append(f"beat {b['n']}: {c} sentence >12 words: {s[:50]}")
                if c == "bean":
                    bean_lines.append(it["text"])
                if b["n"] == 1 and c == "ollie" and meta.get("big_question") and meta["big_question"].lower() in it["text"].lower():
                    first_kid_q = True
            else:
                o = it["opts"]
                if o.get("glow") and o["glow"] not in GLOW:
                    errs.append(f"beat {b['n']}: bad glow {o['glow']}")
                if o.get("glow"):
                    glows += 1
                for k in o:
                    if k in CHARS and o[k] not in EMOTIONS:
                        errs.append(f"beat {b['n']}: bad emotion {o[k]} for {k}")
    for b in beats:
        if b["n"] == 2:
            continue
        for sh in group_shots([i for i in b["items"] if i["type"] != "unparsed"]):
            shots += 1
            secs += shot_seconds(sh)
    shots += 8  # fixed theme sequence
    secs += 30 + 20  # theme + outro
    if shots < 60 or shots > 80:
        errs.append(f"shot count {shots} outside 60-80")
    if not (360 <= secs <= 510):
        errs.append(f"estimated runtime {secs/60:.1f} min outside 6:00-8:30")
    if not first_kid_q:
        errs.append("beat 1: Ollie must ask the exact Big Question")
    if len(bean_lines) < 1 or len(bean_lines) > 3:
        errs.append(f"bean should speak 1-3 times, spoke {len(bean_lines)}")
    for t in bean_lines:
        if words(t) > 2:
            errs.append(f"bean line too long: {t}")
    if not any(meta.get("bean_word", "").strip("!? ").lower() in t.lower() for t in bean_lines):
        errs.append("bean must say her bean_word")
    if glows < 2:
        errs.append("need >=2 luna glow moments")
    return {"meta": meta, "shots": shots, "est_minutes": round(secs / 60, 2), "errors": errs, "warnings": warns}


if __name__ == "__main__":
    ok = True
    for p in sys.argv[1:]:
        r = lint(p)
        print(json.dumps({"file": p, "shots": r["shots"], "est_minutes": r["est_minutes"], "errors": r["errors"]}, indent=1))
        ok &= not r["errors"]
    sys.exit(0 if ok else 1)
