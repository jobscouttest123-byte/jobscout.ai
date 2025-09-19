# JobScoutAI

AI-powered job scout that collects jobs from Remotive, Adzuna, RSS feeds, and EthicalJobs (via Gmail alerts),
filters by your preferences, scores for values alignment (OpenAI), and emails a daily digest.

## Quick Start (GitHub Actions)

1. Upload this repo to GitHub.
2. Add repository **Secrets** (Settings → Secrets and variables → Actions):
   - `GMAIL_USER` = your Gmail address (IMAP enabled)
   - `GMAIL_PASS` = 16‑digit Gmail **App Password**
   - `OPENAI_API_KEY` = OpenAI key
   - (optional) `OPENAI_MODEL` = `gpt-5-mini`
   - (optional) `ADZUNA_ID`, `ADZUNA_KEY`
3. Edit `config.yaml`:
   - Set `testing: false`
   - Set `email.to` to your inbox
4. The workflow `.github/workflows/jobscout-daily.yml` runs **09:00 UTC** daily. Adjust the `cron` if needed.
5. Manually test: Actions → *JobScout Daily* → **Run workflow**.

## Local / Replit
- Install deps: `pip install -r requirements.txt`
- Add env vars as secrets in Replit (🔑) or `.env` locally
- Run: `python daily_runner.py`

## Files
- `collectors/` — remotive, adzuna, rss, ethicaljobs_gmail
- `core/` — normalize, filters, scorer, emailer, pick
- `daily_runner.py` — orchestrator
- `feeds.yaml` — add your RSS feeds
- `config.yaml` — email + filters
