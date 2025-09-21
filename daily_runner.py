import yaml
from collectors.remotive import fetch_remotive
from collectors.adzuna import fetch_adzuna
from collectors.rss_feeds import fetch_from_feeds
# --- EthicalJobs disabled (stub) ---
def fetch_ethicaljobs_from_gmail(*args, **kwargs):
    # Temporarily return nothing so the rest of the pipeline runs
    return []
# -----------------------------------

from core.normalize import normalize
from core.filters import filter_jobs
from core.scorer import score_job
from core.pick import pick_top
from core.emailer import send_email

def load_cfg():
    with open("config.yaml") as f:
        return yaml.safe_load(f)

def load_feeds():
    try:
        with open("feeds.yaml") as f:
            data = yaml.safe_load(f) or {}
            return data.get("feeds", [])
    except FileNotFoundError:
        return []

def collect_all():
    raw = []
    raw += [(j,"remotive") for j in fetch_remotive()]
    raw += [(j,"adzuna") for j in fetch_adzuna("au")]
    raw += [(j,"adzuna") for j in fetch_adzuna("gb")]
    for feed in load_feeds():
        url = feed.get("url")
        label = feed.get("label","rss")
        if url:
            for j in fetch_from_feeds([url], source_label=label):
                raw.append((j,label))
    # raw += [(j, "ethicaljobs_gmail") for j in fetch_ethicaljobs_from_gmail()]  # DISABLED

    jobs = []
    for j,s in raw:
        if s in ("remotive","adzuna"):
            jj = normalize(j,s)
            if jj: jobs.append(jj)
        else:
            jobs.append(j)
    return jobs

def main():
    cfg = load_cfg()
    jobs = filter_jobs(collect_all(), cfg)

    # Cap scored jobs to keep costs minimal
    jobs = jobs[:25]

    for j in jobs:
        s = score_job(j)
        j["llm_score"] = s.get("score_total", 0)
        j["llm_reasons"] = s.get("reasons", [])
        j["red_flags"] = s.get("red_flags", [])
        j["must_ask"] = s.get("must_ask", [])

    picks = pick_top(jobs, cfg.get("results_per_day", 3))

    lines = ["Top picks for today:\n"]
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
