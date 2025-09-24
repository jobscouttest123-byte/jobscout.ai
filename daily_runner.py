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

    # RSS feeds (optional)
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

    # Normalize EVERYTHING to the same schema
    jobs = []
    for j, s in raw:
        try:
            jj = normalize(j, s)
            if jj:
                jobs.append(jj)
        except Exception as e:
            print(f"[normalize] {s} failed: {e}")
    return jobs

# ---------------------------
# Main pipeline
# ---------------------------
def main():
    cfg = load_cfg()

    # 1) Collect all jobs
    collected = collect_all(cfg)
    total_collected = len(collected)

    # 2) Apply filters
    jobs = filter_jobs(collected, cfg)
    kept_after_filters = len(jobs)

    # 3) Cap scored jobs to control cost/time
    jobs = (jobs or [])[:25]

    # 4) Score
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

    # 5) Pick top N
    results_per_day = cfg.get("results_per_day", 3)
    picks = pick_top(jobs, results_per_day) or []
    picked_count = len(picks)

    # 6) Build email
    header = [
        "Top picks for today:",
        f"- Collected: {total_collected}",
        f"- Matched filters: {kept_after_filters}",
        f"- Included in this email (top {results_per_day}): {picked_count}",
        ""
    ]

    lines = []
    if not picks:
        lines.append("No jobs found today.")
    else:
        for p in picks:
            mode = p.get("work_mode", "unspecified").capitalize()
            posted = p.get("posted_at") or "Unknown date"
            lines += [
                f"{p.get('title', 'Unspecified role')} @ {p.get('company', 'Unknown')}",
                f"Link: {p.get('link', '')}",
                f"Source: {p.get('source','unknown')} | Work mode: {mode} | Posted: {posted}",
            ]
            if p.get("llm_reasons"):
                lines.append("Why this matches your values: " + "; ".join(p["llm_reasons"]))
            if p.get("red_flags"):
                lines.append("Red flags: " + "; ".join(p["red_flags"]))
            if p.get("must_ask"):
                lines.append("Questions to ask: " + "; ".join(p["must_ask"]))
            lines.append("")

    body = "\n".join(header + lines)

    # 7) Send
    send_email(cfg, "JobScoutAI — Daily Top Picks", body)


if __name__ == "__main__":
    main()
