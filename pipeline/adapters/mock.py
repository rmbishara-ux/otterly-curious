"""Offline stand-ins for testing the pipeline. Output is placeholder content, never publishable."""
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw
from ..common import ROOT
from .base import Adapter, Unavailable


class MockImage(Adapter):
    name = "mock"

    def generate(self, req, out):
        W, H = 1920, 1080
        plate = ROOT / req["plate"]
        im = Image.open(plate).convert("RGB").resize((W, H)) if plate.exists() else Image.new("RGB", (W, H), (180, 210, 240))
        refs = [ROOT / r for r in req["references"] if (ROOT / r).exists()]
        for i, r in enumerate(refs):
            c = Image.open(r).convert("RGB")
            c = c.crop((0, int(c.height * 0.1), c.width // 4, int(c.height * 0.95))).resize((260, 520))
            im.paste(c, (80 + i * 280, H - 560))
        ImageDraw.Draw(im).text((20, 20), "MOCK", fill=(255, 255, 255))
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        im.save(out)
        return 0.0


class MockVideo(Adapter):
    name = "mock"

    def generate(self, req, out):
        raise Unavailable("mock video provider: use Ken Burns fallback")


class MockVoice(Adapter):
    name = "mock"

    def generate(self, req, out):
        dur = max(0.6, len(req["text"].split()) / 2.6 + 0.2)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"sine=frequency=220:duration={dur:.2f}",
                        "-af", "volume=0.15", str(out)], check=True)
        return 0.0


class MockMusic(Adapter):
    name = "mock"

    def generate(self, req, out):
        dur = req.get("seconds", 30)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"sine=frequency=330:duration={dur}",
                        "-af", "volume=0.05", str(out)], check=True)
        return 0.0
