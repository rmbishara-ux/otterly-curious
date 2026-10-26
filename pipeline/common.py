"""Shared paths, config, logging and caching for the Otterly Curious pipeline."""
import hashlib, json, os, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHARACTERS = ["ollie", "pip", "gran_mari", "gus", "bean", "luna"]
LOCATION_DESC = {
    "kelp_shallows": "a sunny shallow underwater kelp forest in a rocky cove, swaying rounded kelp, soft light shafts, sandy floor",
    "tide_pools": "a sunny rocky shoreline with round tide pools, starfish, anemones and tiny snails, wet sand, the sea in the distance",
    "lighthouse_point": "a grassy rocky point with a cozy red-and-white striped lighthouse, wooden porch, rocking chair, flowers, the harbor with a far-off buoy and boat",
    "driftwood_playground": "a sandy beach playground of smooth driftwood: climbing arch, log see-saw, rope swing, sand mound, shells, calm sea behind",
    "wonder_shed": "a beached wooden rowboat clubhouse under a patchwork tarp, string lights, shelves of shells, stones, feathers, sea glass and a magnifying glass",
}
TIME_DESC = {"morning": "bright morning light", "golden": "warm golden-hour light", "night": "soft moonlit night with a gentle lighthouse beam, still cozy and not dark"}


def load_env():
    f = ROOT / ".env"
    if f.exists():
        for line in f.read_text().splitlines():
            if line.strip() and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def ep_dir(ep):
    d = ROOT / "episodes" / ep
    for sub in ("shots", "audio", "renders", "final", "queue", "book"):
        (d / sub).mkdir(parents=True, exist_ok=True)
    return d


def read_json(p, default=None):
    p = Path(p)
    return json.loads(p.read_text()) if p.exists() else default


def write_json(p, obj):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text(json.dumps(obj, indent=2, ensure_ascii=False))


def stable_seed(*parts):
    return int(hashlib.sha256("|".join(map(str, parts)).encode()).hexdigest()[:8], 16)


def req_hash(req):
    return hashlib.sha256(json.dumps(req, sort_keys=True, default=str).encode()).hexdigest()[:16]


class Cache:
    """Skip regeneration when the request hash and the output file are unchanged."""

    def __init__(self, ep):
        self.path = ROOT / "logs" / f"{ep}_cache.json"
        self.data = read_json(self.path, {})

    def hit(self, key, req, out):
        return self.data.get(key) == req_hash(req) and Path(out).exists()

    def put(self, key, req):
        self.data[key] = req_hash(req)
        write_json(self.path, self.data)


class CostLog:
    """Every generation is logged with prompt, seed, provider, cost and output path."""

    def __init__(self, ep):
        self.ep = ep
        self.path = ROOT / "logs" / f"{ep}_generations.jsonl"
        self.path.parent.mkdir(exist_ok=True)

    def log(self, stage, provider, prompt, seed, cost, out, unit="credits"):
        rec = dict(ts=time.strftime("%Y-%m-%dT%H:%M:%S"), ep=self.ep, stage=stage, provider=provider,
                   prompt=prompt, seed=seed, cost=cost, unit=unit, output=str(out))
        with open(self.path, "a") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    def total(self):
        if not self.path.exists():
            return 0.0
        return sum(json.loads(l)["cost"] for l in self.path.read_text().splitlines() if l.strip())

    def check_budget(self, projected=0.0):
        cap = os.environ.get("EPISODE_BUDGET_CREDITS")
        if cap and self.total() + projected > float(cap):
            raise SystemExit(f"BUDGET STOP: {self.total() + projected:.1f} > cap {cap} credits")


def font_path():
    for d in (ROOT / "assets" / "fonts",):
        for pat in ("Fredoka*.ttf", "Nunito*.ttf"):
            for f in d.glob(pat):
                if f.stat().st_size > 10000:
                    return str(f)
    for f in ("/usr/share/fonts/truetype/inter/Inter-Bold.ttf", "/usr/share/fonts/opentype/inter/Inter-Bold.otf"):
        if Path(f).exists():
            return f
    import subprocess
    out = subprocess.run(["fc-match", "-f", "%{file}", "Inter:bold"], capture_output=True, text=True).stdout
    return out or "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def ttf_font_path():
    """TrueType-outline font for reportlab (which cannot embed OpenType/CFF)."""
    for pat in ("Fredoka*.ttf", "Nunito*.ttf"):
        for f in (ROOT / "assets" / "fonts").glob(pat):
            if f.stat().st_size > 10000:
                return str(f)
    for f in ("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        if Path(f).exists():
            return f
    raise SystemExit("no TrueType font found; add one to assets/fonts/")
