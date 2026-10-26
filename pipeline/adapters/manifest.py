import json
from pathlib import Path
from ..common import ep_dir
from .base import Adapter, Pending


class _Manifest(Adapter):
    kind = "x"
    name = "manifest"

    def generate(self, req, out):
        out = Path(out)
        q = ep_dir(self.ep) / "queue"
        q.mkdir(exist_ok=True)
        f = q / f"{self.kind}_{out.stem}.json"
        f.write_text(json.dumps({"kind": self.kind, "output": str(out), "request": req}, indent=2))
        raise Pending(f"{self.kind} request queued: {f.name}")


class ManifestImage(_Manifest):
    kind = "image"


class ManifestVideo(_Manifest):
    kind = "video"


class ManifestVoice(_Manifest):
    kind = "voice"


class ManifestMusic(_Manifest):
    kind = "music"
