"""Write captions for the vertical Shorts (final/EXX_short_demo.srt, EXX_short_fail.srt) using the same shot selection as assemble()."""
import sys
from pipeline.assemble import load_sb, timeline, srt_time, ep_dir


def short_srt(ep, tag):
    sb = load_sb(ep)
    timeline(sb)
    picked = [s for s in sb["shots"] if tag in s["tags"]]
    cap = 29.5 if tag == "short_fail" else 59.5
    while len(picked) > 1 and sum(s["duration"] for s in picked) > cap:
        picked.pop(0 if tag == "short_fail" else -1)
    cues, n, t = [], 0, 0.0
    for s in picked:
        for l in s["dialogue"]:
            n += 1
            a = t + l.get("start", 0.5)
            b = min(a + l.get("length", 2.0), t + s["duration"])
            who = l["char"].replace("_", " ").title()
            cues.append(f"{n}\n{srt_time(a)} --> {srt_time(b)}\n{who}: {l['text']}\n")
        t += s["duration"]
    out = ep_dir(ep) / "final" / f"{ep}_{tag}.srt"
    out.write_text("\n".join(cues))
    return out, n, round(t, 1)


if __name__ == "__main__":
    for ep in sys.argv[1:] or ["E01", "E02", "E03", "E04", "E05"]:
        for tag in ("short_demo", "short_fail"):
            print(ep, tag, *short_srt(ep, tag))
