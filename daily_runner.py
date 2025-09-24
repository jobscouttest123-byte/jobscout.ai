# daily_runner.py
import os
import yaml
from collectors.remotive import fetch_remotive
from collectors.adzuna import fetch_adzuna
from collectors.rss_feeds import fetch_from_feeds
from core.normalize import normalize
from core.filters import filter_jobs
from core.scorer import score_job
from core.pick import pick_top
from core.emailer import send_email

# ---------------------------
# Config loader (respects CONFIG_FILE; falls back to config.yaml)
# ---------------------------
def load_cfg():
    path = os.getenv("CONFIG_FILE", "config.yaml")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

# ---------------------------
# Load extra feeds if any (optional)
# ---------------------------
def load_feeds():
    try:
        with open("feeds.yaml", "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            return data.get("feeds", [])
    except FileNotFoundError:
        return []

# ---------------------------
# Collect jobs from configured sources
# ---------------------------
def collect_all(cfg):
    raw = []

    # Remotive
    try:
        for j in fetch_remotive():
            raw.append((j, "remotive"))
    except Exception as e:
        print(f"[collect] remotive failed: {e}")

    # Adzuna for configured countries (default AU + UK)
    cc_map = {"AU": "au", "UK": "gb", "GB": "gb"}
    for country in (cfg.get("allowed_countries") or ["AU", "UK"]):
        code = cc_map.get(str(country).upper())
        if not code:
            continue
        try:
            for j in fetch_adzuna(code):
                raw.append((j, "adzuna"))
        except Exception as e:
            print(f"[collect] adzuna({code}) failed: {e}")

    # RSS feeds
    for feed in load_feeds():
        url = (feed or {}).get("url")
        label = (feed or {}).get("label", "rss")
        if not url:
            continue
        try:
            for j in fetch_from_feeds([url], source_label=label):
                raw.append((j, label))
        except Exception as e:
            print(f"[collect] rss {label} failed: {e}")

    # Normalize
    jobs = []
    for j, s in raw:
        if s in ("remotive", "adzuna"):
            jj = normalize(j, s)
            if jj:
                jobs.append(jj)
        else:
            jobs.append(j)
    return jobs

# ---------------------------
# Main pipeline
# ---------------------------
def main():
    cfg = load_cfg()

    jobs = collect_all(cfg)
    jobs = filter_jobs(jobs, cfg)

    # Cap scored jobs to control cost/time
    jobs = (jobs or [])[:25]

    for j in jobs:
        try:
            s = score_job(j) or {}
        except Exception as e:
            print(f"[score] failed: {e}")
            s = {}
        j["llm_score"] = s.get("score_total", 0)
        j["llm_reasons"] = s.get("reasons", [])
        j["red_flags"] = s.get("red_flags", [])
        j["must_ask"] = s.get("must_ask", [])

    picks = pick_top(jobs, cfg.get("results_per_day", 3)) or []

    lines = ["Top picks for today:\n"]
    if not picks:
        lines.append("No jobs found today.")
    else:
        for p in picks:
            lines += [
                f"{p.get('title')} @ {p.get('company')}",
                f"Link: {p.get('link')}",
                f"Source: {p.get('source','rss')} | Remote: {p.get('remote')}",
            ]
            if p.get("llm_reasons"):
                lines.append("Why this matches your values: " + "; ".join(p["llm_reasons"]))
            if p.get("red_flags"):
                lines.append("Red flags: " + "; ".join(p["red_flags"]))
            if p.get("must_ask"):
                lines.append("Questions to ask: " + "; ".join(p["must_ask"]))
            lines.append("")
    body = "\n".join(lines)

    send_email(cfg, "JobScoutAI — Daily Top Picks", body)

if __name__ == "__main__":
    main()
