"""ElevenLabs text-to-speech adapter. UNTESTED (no API key was available when written).
Needs ELEVENLABS_API_KEY in .env and a voice_id per character in bible/voice_configs.json. Settings are fixed per character."""
import json, os, urllib.request
from pathlib import Path
from ..common import ROOT, load_env
from .base import Adapter


class ElevenLabsVoice(Adapter):
    name = "elevenlabs"

    def generate(self, req, out):
        load_env()
        key = os.environ.get("ELEVENLABS_API_KEY")
        cfg = json.loads((ROOT / "bible" / "voice_configs.json").read_text())[req["char"]]
        if not key or not cfg.get("voice_id"):
            raise SystemExit("ElevenLabs needs ELEVENLABS_API_KEY and a voice_id for this character")
        body = json.dumps({"text": req["text"], "model_id": "eleven_multilingual_v2",
                           "voice_settings": cfg.get("settings", {"stability": 0.5, "similarity_boost": 0.8})}).encode()
        r = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{cfg['voice_id']}", data=body,
                                   headers={"xi-api-key": key, "Content-Type": "application/json", "Accept": "audio/mpeg"})
        Path(out).write_bytes(urllib.request.urlopen(r, timeout=60).read())
        return len(req["text"]) / 1000.0
