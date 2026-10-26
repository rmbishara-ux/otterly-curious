import json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pipeline import script_format, storyboard

ROOT = Path(__file__).resolve().parent.parent


class Scripts(unittest.TestCase):
    def test_all_scripts_lint_clean(self):
        for i in range(1, 11):
            r = script_format.lint(ROOT / "episodes" / f"E{i:02d}" / "script.md")
            self.assertEqual(r["errors"], [], f"E{i:02d}")

    def test_lint_catches_long_kid_sentence(self):
        p = ROOT / "tests" / "_bad.md"
        src = (ROOT / "episodes" / "E01" / "script.md").read_text().replace(
            "OLLIE (curious): It was right here yesterday!", "OLLIE (curious): It was right here yesterday and now it is not here anymore at all!")
        p.write_text(src)
        try:
            self.assertTrue(any(">12 words" in e for e in script_format.lint(p)["errors"]))
        finally:
            p.unlink()


class Storyboards(unittest.TestCase):
    def test_storyboard_shape(self):
        for i in range(1, 11):
            sb = storyboard.build(f"E{i:02d}")
            self.assertTrue(60 <= sb["shot_count"] <= 80)
            self.assertTrue(360 <= sb["total_seconds"] <= 510)
            ids = [s["id"] for s in sb["shots"]]
            self.assertEqual(len(ids), len(set(ids)))
            self.assertTrue(any("short_fail" in s["tags"] for s in sb["shots"]))
            self.assertTrue(any("short_demo" in s["tags"] for s in sb["shots"]))
            self.assertTrue(all(s["location"] for s in sb["shots"]))


if __name__ == "__main__":
    unittest.main()
