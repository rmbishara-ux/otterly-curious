#!/usr/bin/env python3
"""Single entry point: python3 pipeline/run.py E01 [--stages script,storyboard,images,animate,voice,music,assemble,qa,package]

Providers come from env (IMAGE_PROVIDER etc.; see pipeline/adapters/__init__.py). Default 'manifest' queues requests.
Set QUALITY=draft for a fast 960x540 test render. Prints the running cost total after each stage and stops on budget overrun."""
import argparse, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pipeline.common import load_env, CostLog, ep_dir  # noqa: E402
from pipeline import script_format, storyboard, stages, assemble as asm, qa, package as pkg  # noqa: E402

ORDER = ["script", "storyboard", "images", "animate", "voice", "music", "assemble", "qa", "package"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("episode")
    ap.add_argument("--stages", default=",".join(ORDER))
    a = ap.parse_args()
    load_env()
    ep, want = a.episode, a.stages.split(",")
    ep_dir(ep)
    log = CostLog(ep)
    assembled = None
    for st in ORDER:
        if st not in want:
            continue
        print(f"== {st}")
        if st == "script":
            r = script_format.lint(ep_dir(ep) / "script.md")
            if r["errors"]:
                print(json.dumps(r["errors"], indent=1))
                sys.exit("script lint failed")
            print(f"script ok: {r['shots']} shots, ~{r['est_minutes']} min")
        elif st == "storyboard":
            sb = storyboard.build(ep)
            print(f"{sb['shot_count']} shots, {sb['total_seconds']}s")
        elif st == "images":
            if stages.run_images(ep):
                sys.exit("images queued in episodes/%s/queue/; fulfil them, then re-run" % ep)
        elif st == "animate":
            stages.split_long(ep)
            stages.run_animate(ep)
        elif st == "voice":
            stages.run_voice(ep)
        elif st == "music":
            stages.run_music(ep)
        elif st == "assemble":
            assembled = asm.assemble(ep)
            print(json.dumps(assembled, indent=1))
        elif st == "qa":
            if assembled is None:
                sys.exit("run assemble in the same invocation before qa")
            rep = qa.run_qa(ep, assembled)
            print(("PASS" if rep["passed"] else "FAIL"), json.dumps([c for c in rep["checks"] if not c["pass"]], indent=1))
        elif st == "package":
            print("title:", pkg.package(ep))
        print(f"-- running cost: {log.total():.2f} credits")


if __name__ == "__main__":
    main()
