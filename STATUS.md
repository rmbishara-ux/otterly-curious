# STATUS (Oct 26, 2026)

## Cost
Higgsfield credits spent: 122 (988.1 -> 866.1). Character-sheet phase ~98 of the 300 cap; bible plates ~20; banner ~4. No episode footage generated yet. No per-episode budget was provided; the pipeline reads EPISODE_BUDGET_CREDITS from .env and stops if the projection exceeds it.
Rough projection for a real E01: ~64 stills (~2-8 credits each, ~130-500) + 64 image-to-video clips (video credits not yet quoted; get a quote before running) + voice + music. Quote first.

## Done
- Cast approved (6 characters, soft-3D style): characters/<name>/ turnarounds, expressions, Bean float pose, Luna glow steps
- Bible: series bible, style guide v2, voice configs (voice IDs TBD), songs (lyrics + prompts, no audio), 5 location hero plates
- All 10 Season One scripts (episodes/E01-E10/script.md); every one passes pipeline/script_format.py (60-80 shots, 6.4-7.2 min est, Big Question, value, demo, rules). Storyboard JSON for all 10.
- Pipeline code: script lint, storyboard, prompts, adapters (mock, manifest, ElevenLabs untested), cache + cost log, Ken Burns fallback, assembly (ffmpeg, burned-in Big Question, embedded SRT, 2 vertical Shorts), QA (8 checks), packaging. Tested end to end on E01 with MOCK providers only (placeholder media): all 8 QA checks passed, which proves the plumbing, not episode quality.
- YouTube: youtube.md for all 10, thumbnails for E01-E10 (E01 verified visually), 10-week content calendar (first date 2026-12-05, Sat 9:00 PT), keyword notes
- E01 picture book: text (634 words, 13 spreads), print PDF (32 pp, 8.75in with bleed), ebook PDF, EPUB, validation report. Art is PLACEHOLDER.
- Channel kit for @OtterlyCurious123 (channel/): about copy, keywords, avatar, banner, watermark, playlists, trailer plan, launch checklist

## Not done / blocked (needs a person or a decision)
1. REAL E01 production: images, image-to-video, voice, music have not been generated. Needs: voice provider + voice IDs (bible/voice_configs.json), a music source (Suno has no official API; Higgsfield generate_audio is available via this session), video-credit quote, and a per-episode budget.
2. The channel is NOT connected to vidIQ here (connected channels belong to other projects). Nothing has been uploaded or edited on @OtterlyCurious123. Owner must authorize via the link in chat, or apply channel/ by hand.
3. Fonts: Nunito/Fredoka could not be downloaded (network); book/thumbnails use fallback fonts. Drop the TTFs in assets/fonts/.
4. Book print art: needs 5250x2625 px per spread (300 dpi); current PDF uses placeholders.
5. Known cast issues: Bean's face too close to Ollie's in close-ups; Gran Mari reads bald; Ollie's tuft leans back. Pip's new teacup (with lid) needs a Season 2 sheet (E10).
6. Depth layers + time-of-day variants for the 5 plates not made. Lighthouse lamp room is out of frame (E06 needs it).
7. Script judgment calls flagged by the writers (science simplifications) are in each script's audit_note; a human should skim E02, E05, E06, E08 and E09 especially.
8. Book spreads: automated sentence count is max 4 per spread (dialogue-heavy), brief says 1-3.
