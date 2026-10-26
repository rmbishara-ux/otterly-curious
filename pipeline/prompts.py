"""Shot prompt = style prefix + character fragments + scene + action + camera. Never freehand a character."""
from .common import ROOT, LOCATION_DESC, TIME_DESC, stable_seed

CAMERA = {
    "static": "static medium shot", "wide": "wide establishing shot", "close": "close-up shot", "slow_push": "slow push-in medium shot",
    "pan_right": "gentle pan to the right", "pan_up": "tilt up from low angle", "tilt_up": "tilt up to the sky", "follow": "tracking shot following the characters",
    "top_down": "top-down close view", "timelapse": "wide shot, time passing, long shadows",
}
GLOW = {"dim": "Luna glows very softly", "bright": "Luna glows noticeably brighter, warm white", "sparkle": "Luna glows radiant white with small star sparkles around her"}


def _read(p):
    return (ROOT / p).read_text().strip()


def fragment(name):
    return _read(f"characters/{name}/prompt_fragment.md")


def ref_images(shot):
    refs = [f"characters/{c}/{c}_turnaround.png" for c in shot["characters"]]
    plate = f"bible/locations/{shot['location']}.png"
    return refs, plate


def shot_prompt(shot):
    style = _read("prompts/style_prefix.md")
    chars = " ".join(f"{fragment(c)} Expression: {e}." for c, e in shot["characters"].items())
    scene = f"Location: {LOCATION_DESC[shot['location']]}. Lighting: {TIME_DESC.get(shot['time'], shot['time'])}."
    glow = GLOW.get(shot["luna_glow"], "")
    cam = CAMERA.get(shot["camera"], shot["camera"])
    action = shot["action"] or "The characters continue the conversation, reacting naturally."
    book = " Leave a calm, uncluttered area in the upper third for book text." if shot.get("book_safe") else ""
    text = f"{style}\nCharacters (keep EXACTLY as the reference images): {chars}\n{scene}\nAction: {action} {glow}\nCamera: {cam}.{book}\n16:9 frame."
    return {"prompt": text, "negative": _read("prompts/negative.md"), "seed": stable_seed(shot["id"], "img"),
            "references": ref_images(shot)[0], "plate": ref_images(shot)[1], "aspect": "16:9"}


def motion_prompt(shot):
    return (f"{CAMERA.get(shot['camera'], 'static')}, gentle character motion in simple arcs, soft blinking and breathing, "
            f"{shot['action'][:140]} Keep characters on model, no morphing, no new characters.")
