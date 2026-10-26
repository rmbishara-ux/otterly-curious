"""Provider adapters. The pipeline only talks to these interfaces; swap providers with env vars:
IMAGE_PROVIDER, VIDEO_PROVIDER, VOICE_PROVIDER, MUSIC_PROVIDER = mock | manifest | elevenlabs (voice only).

mock      offline stand-ins so the whole pipeline can be exercised and tested (NOT for publishing).
manifest  writes each generation request to episodes/EXX/queue/*.json and stops; a human or an agent session with
          the provider's tools (e.g. the Higgsfield connector) fulfils them, then re-run the stage to ingest results.
"""
import os
from .base import Pending, Unavailable
from .mock import MockImage, MockVideo, MockVoice, MockMusic
from .manifest import ManifestImage, ManifestVideo, ManifestVoice, ManifestMusic
from .elevenlabs import ElevenLabsVoice

_REG = {
    "image": {"mock": MockImage, "manifest": ManifestImage},
    "video": {"mock": MockVideo, "manifest": ManifestVideo},
    "voice": {"mock": MockVoice, "manifest": ManifestVoice, "elevenlabs": ElevenLabsVoice},
    "music": {"mock": MockMusic, "manifest": ManifestMusic},
}


def get(kind, ep):
    name = os.environ.get(f"{kind.upper()}_PROVIDER", "manifest")
    if name not in _REG[kind]:
        raise SystemExit(f"unknown {kind} provider '{name}'. options: {sorted(_REG[kind])}")
    return _REG[kind][name](ep)
