# Otterly Curious
AI-generated 2D/3D animated kids' science series (ages 3-7). Every big question starts with "Let's find out!"
Channel: https://www.youtube.com/@OtterlyCurious123 (kit in channel/). See STATUS.md for what is done and what is next.

## Layout
bible/ (series bible, style guide v2 soft-3D, songs, voice configs, location plates) | characters/ (approved sheets, expressions) |
episodes/EXX/ (script.md, storyboard.json, youtube.md, book/) | pipeline/ (stages + adapters) | prompts/ | book/ | youtube/ | channel/ | logs/ | tests/

## Run
    python3 -m unittest tests.test_pipeline          # lint all 10 scripts, build all storyboards
    python3 pipeline/run.py E01 --stages script,storyboard
    IMAGE_PROVIDER=mock VOICE_PROVIDER=mock MUSIC_PROVIDER=mock VIDEO_PROVIDER=mock QUALITY=draft python3 pipeline/run.py E01   # plumbing test only
    python3 book/build.py E01                          # print PDF (bleed), ebook PDF, EPUB, validation.md
    python3 youtube/calendar.py [first-Saturday]       # 10-week calendar
Providers: IMAGE_PROVIDER / VIDEO_PROVIDER / VOICE_PROVIDER / MUSIC_PROVIDER = mock | manifest | elevenlabs (voice). `manifest` writes
requests to episodes/EXX/queue/ for a human or agent session with the provider's tools to fulfil, then re-run. Keys live in .env (never committed).
