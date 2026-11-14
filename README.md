# nfp-social — Noida Farmhouse Party social autopilot

Everything for Instagram, Facebook, Threads and YouTube from **15 Nov 2026 to 15 May 2027**, posted automatically by GitHub Actions.

| Time (IST) | What | Platform |
|---|---|---|
| 09:23 | Daily story (`media/story`) | Instagram + Facebook |
| 12:27 | 2nd daily post: carousel on reel days, reel on post days (`*_b*.jpg`) | Instagram + Facebook |
| 12:56 | Daily text post | Threads |
| 17:57 | Daily Short + thumbnail (`media/video`, `media/thumb`) | YouTube |
| 19:26 | Reel Mon/Wed/Fri/Sun · carousel Tue/Sat · single image Thu | Instagram + Facebook |

- `content/plan.json` / `calendar.csv` — all 182 days: captions, titles, Threads text, landing pages.
- `media/` — served publicly by GitHub Pages (the APIs fetch media from these URLs).
- `creatives/highlight` — 8 Instagram highlight covers (set them in the Instagram app). `creatives/ads` + `ADS_COPY.md` — Meta ad sets.
- `publish/publish.py` — the publisher (only today's item, never back-fills, never boosts or pays). `state/posted.json` stops duplicates; `state/cutoff.json` skips days already scheduled in Business Suite / Studio / Threads.
- `tools/` — creative factory. Add photos to `photos/` (same naming) and run **Actions → render-creatives**.
- One-time setup of the secrets: see `SETUP.md`. Test anytime: **Actions → publish → Run workflow → task: check**.

No tokens or passwords are stored in this repo — only in GitHub Secrets.
