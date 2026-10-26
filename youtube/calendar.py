"""Ten-week release calendar: one episode per week, two Shorts spaced across the following days.
python3 youtube/calendar.py [YYYY-MM-DD first Saturday]   (default 2026-12-05, 9:00 AM Pacific)

Timing is an assumption (weekend morning, when kids' co-viewing is highest); revisit with channel analytics after 3-4 uploads."""
import sys, json, datetime as dt
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pipeline.script_format import parse

ROOT = Path(__file__).resolve().parent.parent
start = dt.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else dt.date(2026, 12, 5)
assert start.weekday() == 5, "start date must be a Saturday"
rows = []
for i in range(1, 11):
    ep = f"E{i:02d}"
    meta, _ = parse(ROOT / "episodes" / ep / "script.md")
    d0 = start + dt.timedelta(weeks=i - 1)
    rows.append({"episode": ep, "title": f"{meta['big_question']} | Otterly Curious", "value": meta["value"], "book": meta["book_title"],
                 "episode_date": d0.isoformat(), "episode_time": "09:00 PT (Sat)",
                 "short_demo_date": (d0 + dt.timedelta(days=3)).isoformat(), "short_demo_time": "09:00 PT (Tue)",
                 "short_fail_date": (d0 + dt.timedelta(days=5)).isoformat(), "short_fail_time": "09:00 PT (Thu)"})
(ROOT / "youtube" / "content_calendar.json").write_text(json.dumps(rows, indent=2))
md = ["# Content calendar (10 weeks)", "", "Rules: same weekday and time every week; all uploads made-for-kids; no links, QR, or merch mentions; captions from script.", "",
      "| Ep | Episode (Sat 9:00 PT) | Demo Short (Tue) | Fail Short (Thu) | Big Question | Value |", "|---|---|---|---|---|---|"]
for r in rows:
    md.append(f"| {r['episode']} | {r['episode_date']} | {r['short_demo_date']} | {r['short_fail_date']} | {r['title'].split(' | ')[0]} | {r['value']} |")
md += ["", "Production lead: E01 final render needed ~2 weeks before the first date; bank at least 3 finished episodes before launch.",
       "Each episode differs in question, location mix, and demo (see episodes/*/script.md) to stay clear of repetitive-content enforcement."]
(ROOT / "youtube" / "content_calendar.md").write_text("\n".join(md) + "\n")
print("\n".join(md))
