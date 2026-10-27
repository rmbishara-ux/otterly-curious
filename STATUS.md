# STATUS (Oct 26, 2026)

## Cost
Higgsfield credits: 988.1 at start of project. Pre-production (sheets, plates, banner) 122 -> 866.1. Real E01 production: 862.5 -> 436.1 = 426.4 credits (voice ~13; 62 first-pass stills 124 incl. ~108 wasted by the reference-inset bug, then 54 re-rolls ~108; 20 Kling 3.0 Pro 5 s silent hero clips = 175). E01 is inside the 700-credit cap with ~270 to spare; balance 436.1.
Per-episode estimate going forward: ~62 stills (124, with the inset-bug fix no re-roll needed) + voice ~13 + ~20 hero clips (175) = ~310 credits.

## Done
- Cast approved (6 characters, soft-3D style): characters/<name>/ turnarounds, expressions, Bean float pose, Luna glow steps
- Bible: series bible, style guide v2, voice configs (voice IDs TBD), songs (lyrics + prompts, no audio), 5 location hero plates
- All 10 Season One scripts (episodes/E01-E10/script.md); every one passes pipeline/script_format.py (60-80 shots, 6.4-7.2 min est, Big Question, value, demo, rules). Storyboard JSON for all 10.
- Pipeline code: script lint, storyboard, prompts, adapters (mock, manifest, ElevenLabs untested), cache + cost log, Ken Burns fallback, assembly (ffmpeg, burned-in Big Question, embedded SRT, 2 vertical Shorts), QA (8 checks), packaging. Tested end to end on E01 with MOCK providers only (placeholder media): all 8 QA checks passed, which proves the plumbing, not episode quality.
- YouTube: youtube.md for all 10, thumbnails for E01-E10 (E01 verified visually), 10-week content calendar (first date 2026-12-05, Sat 9:00 PT), keyword notes
- E01 picture book: text (634 words, 13 spreads), print PDF (32 pp, 8.75in with bleed), ebook PDF, EPUB, validation report. Art is PLACEHOLDER.
- Channel kit for @OtterlyCurious123 (channel/): about copy, keywords, avatar, banner, watermark, playlists, trailer plan, launch checklist

## Not done / blocked (needs a person or a decision)
1. E01 CUT WITH MUSIC DONE (episodes/E01/final/E01_episode.mp4, 7:46, 1080p, QA 8/8 PASS; Shorts demo 52 s + fail 25.7 s). Stills, locked voices, 20 Kling hero clips (~25% of runtime), Ken Burns elsewhere, theme song + outro + 5 mood beds (vidIQ music generator, 25 vidIQ credits each = 175 of 821; originals in assets/music/, continuous mix built in assemble.build_music). Theme is 44 s clip faded at 30 s (title sting is cut); outro 58 s faded at 20 s. STILL TO DO: human listen to voices; upload via YouTube Studio (vidIQ cannot publish; connected as @otterlycurious123, channel UCCLZx9rLKy-UJBqsrL5LRaA), then set metadata/thumbnail through vidIQ.
2. E02 (7:18, 'Why do otters hold hands?') and E03 (7:37, 'Where does a rainbow come from?') DONE: QA 8/8 pass, Shorts (E02 demo 57.9 s / fail 21.7 s; E03 demo 53.9 s / fail 27.3 s), story-frame thumbnails, music mixed. 62 stills each (theme, outro and Wonder Pocket recap stills + 6 theme/outro clips reused from E01), locked voices, 8 new Kling Pro hero clips each (+6 reused theme/outro clips). Drift flags eyeballed and logged in episodes/E0x/drift_reviewed.json. Credits: balance 436.1 after E01 -> 52.2 after E02+E03 = 383.9 total (voices ~23, stills ~200 incl. ~10 refunded/failed retries and 1 re-roll, 16 clips 140). Per-episode cost with reuse is ~190. NOT uploaded yet: owner uploads to YouTube Studio (made for kids, captions .srt, thumbnail), then metadata is set through vidIQ (episodes/E0x/youtube.md). Credits left: 52 Higgsfield (top up before E04), vidIQ ~600.
3. SHORTS + EPISODE METADATA SET via vidIQ (all private): E01-E03 long videos (youtu.be/0EmctoqxOms, fYBxn_vdRQM, affD-2yPnc0) and six Shorts (fKhaHFKF19M, IPwNGROvHB4, _aOPBosVTHY, qKcZWS1u-7U, i5vL2Fe8Zgo, yrJ6iWRzAp4) have final titles, descriptions, tags; each Short links to its episode. CHANNEL TRAILER built: channel/trailer/Otterly_Curious_channel_trailer.mp4 (44 s, cut from E01-E03 clips, 2 new Ollie lines ~0.5 credit; script channel/build_trailer.py). Owner uploads it in Studio and sets it as the 'for people who haven't subscribed' video. Still manual in Studio: made-for-kids on every upload (check E02/E03/Shorts), custom thumbnails for E02/E03, captions .srt for E02/E03.
2. The channel is NOT connected to vidIQ here (connected channels belong to other projects). Nothing has been uploaded or edited on @OtterlyCurious123. Owner must authorize via the link in chat, or apply channel/ by hand.
3. Fonts: Nunito/Fredoka could not be downloaded (network); book/thumbnails use fallback fonts. Drop the TTFs in assets/fonts/.
4. Book print art: needs 5250x2625 px per spread (300 dpi); current PDF uses placeholders.
5. Known cast issues: Bean's face too close to Ollie's in close-ups; Gran Mari reads bald; Ollie's tuft leans back. Pip's new teacup (with lid) needs a Season 2 sheet (E10).
6. Depth layers + time-of-day variants for the 5 plates not made. Lighthouse lamp room is out of frame (E06 needs it).
7. Script judgment calls flagged by the writers (science simplifications) are in each script's audit_note; a human should skim E02, E05, E06, E08 and E09 especially.
8. Book spreads: automated sentence count is max 4 per spread (dialogue-heavy), brief says 1-3.
