# Budget and voice plan (prices checked Oct 26, 2026 through the Higgsfield connector; estimates are mine)

## Measured unit costs (connector quotes)
| Item | Cost |
|---|---|
| 2K still, Nano Banana Pro | 2 credits |
| Image-to-video, Kling 3.0 Std, 5 s, silent | 7.5 credits (1.5 / s) |
| Image-to-video, Kling 3.0 Pro, 5 s, silent | 8.75 credits (1.75 / s) |
| Image-to-video, Seedance 2.5, 5 s, 720p | 35 credits (7 / s) - too expensive for a series |
| Voice line, Seed Audio | ~0.2 credits |
| Music | Not available in Higgsfield for standalone use (Suno is not in the catalog). Use Suno directly or a licensed library. |
Credit price: ~5.3 c on top-up packs (2,000 = $105.26; 4,000 = $210.53; 1,000 = $55.56). Plan credits are cheaper: Plus annual $39/mo for 1,000 (~3.9 c); Ultra annual $99/mo for 3,000 (~3.3 c). Top-up credits expire in 90 days.

## Per-episode estimate (E01: 64 shots, ~407 s). ASSUMPTIONS: ~2 attempts per still, +25% video rerolls, ~20 credits of voice retakes.
| Plan | Stills | Video | Voice | Total credits | ~$ at 5.3 c | ~$ at 3.9 c (Plus annual) |
|---|---|---|---|---|---|---|
| Hybrid (AI motion on ~40% of runtime: question, demo, payoff shots; Ken Burns elsewhere) | 256 | 350 | 20 | ~625 | ~$33 | ~$24 |
| Full AI motion on every shot | 256 | 890 | 20 | ~1,165 | ~$62 | ~$45 |
Add for the picture book: ~65-120 credits (13 spreads, regenerate at print resolution + upscale; the upscale was not quoted).
Not credits: music (Suno plan ~$10-30/mo, one-time for the series theme/outro/jingle/6 beds), sound effects from a free/CC0 library, fonts (free).

## Recommended budgets
- E01 pilot cap: 700 credits (set as EPISODE_BUDGET_CREDITS in .env). The current balance (~866) already covers it, so no purchase is needed to start.
- Season One (10 episodes, hybrid): ~6,300 credits, roughly $210-$330 depending on how credits are bought. Do not pre-buy; re-quote after E01 shows the real reroll rate.
- Keep auto-refill OFF for now so a bad run cannot spend more than the cap.
- Review points: after E01 (actual vs estimate), then after E04.

## Voice options
1. Higgsfield seed_audio presets (recommended for now): cheapest, same wallet, repeatable with fixed pitch/speed. Weakness: these are adult preset voices pitch-shifted; child characters may sound artificial. Judge the audition clips.
2. ElevenLabs v4 through Higgsfield or direct (adapter exists, untested): often more expressive; price per line not yet quoted.
3. Human voice actors for Ollie, Pip and Bean (best quality for children's characters; costs money and needs releases/child-performer rules). Consider once the show has an audience.
Whichever you pick: choose once, save voice_id + settings in bible/voice_configs.json, never change. Do not clone a real person's voice without written consent.
Audition files: bible/voice_auditions/ (15 clips, ~3 credits).
