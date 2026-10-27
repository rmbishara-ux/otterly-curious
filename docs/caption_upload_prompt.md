# Prompt: upload captions to YouTube Studio (run in a local Claude Code session with Chrome connected)

Task: upload English caption files to 15 videos on the Otterly Curious YouTube channel (channel ID UCCLZx9rLKy-UJBqsrL5LRaA) using my signed-in YouTube Studio in Chrome. Do not change anything else on the channel: no titles, descriptions, visibility, schedules, thumbnails or audience settings.

Files are in `captions_upload/` of this repo (ryanbishara/otterly-curious). Each file is a timed .srt.

| Video ID | Caption file |
|---|---|
| 0EmctoqxOms | E01_episode.srt |
| fKhaHFKF19M | E01_short_demo.srt |
| IPwNGROvHB4 | E01_short_fail.srt |
| fYBxn_vdRQM | E02_episode.srt |
| _aOPBosVTHY | E02_short_demo.srt |
| qKcZWS1u-7U | E02_short_fail.srt |
| affD-2yPnc0 | E03_episode.srt |
| i5vL2Fe8Zgo | E03_short_demo.srt |
| yrJ6iWRzAp4 | E03_short_fail.srt |
| 1n-ybLnnxHs | E04_episode.srt |
| C31uvFPeOdg | E04_short_demo.srt |
| aF04FhjZSaw | E04_short_fail.srt |
| DPN_-z9n_nw | E05_episode.srt |
| NWuDEF6mFjY | E05_short_demo.srt |
| pRQSHxAZxNc | E05_short_fail.srt |

For each video:
1. Open `https://studio.youtube.com/video/<VIDEO_ID>/translations`.
2. If English already has a caption, delete or replace it with ours; if another language is set as the video language, keep it and just add English.
3. Add language > English > Add under Subtitles > Upload file > "With timing" > choose the matching .srt > Continue.
4. Confirm the caption shows as Published (not Draft) and, for one in every few videos, that the first cue text matches the file.
5. Record the video ID and result (done / failed + reason).

Rules:
- Do E01 episode (0EmctoqxOms) first, then stop and show me the result before doing the other 14.
- If Studio shows an error, a verification prompt, a different layout, or anything unexpected, stop and tell me instead of improvising.
- Work one video at a time; never open more than one Studio tab.
- Finish with a table of all 15 videos and their status.
