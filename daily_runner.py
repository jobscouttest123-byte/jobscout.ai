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
# Config loader (safe + flexible)
# ---------------------------
def load_cfg():
    path = os.getenv("CONFIG_FILE", "config.yaml")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

# ---------------------------
# Load extra feeds if any
# ---------------------------
def load_feeds():
    try:
        with open("feeds.yaml", "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            return data.get("feeds", [])
    except FileNotFoundError:
        return []

# ---------------------------
# Collect jobs from all sources
# ---------------------------
def collect_all():
    raw = []
    raw += [(j, "remotive") for j in fetch_remotive()]
    raw += [(j, "adzuna") for j in fetch_adzuna("au")]
    raw += [(j, "adzuna") for j in fetch_adzuna("gb")]

    for feed in load_feeds():
        url = feed.get("url")
        label = feed.get("label", "rss")
        if url:
            for j in fetch_from_feeds([url], source_label=label):
                raw.append((j, label))

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
# Main job pipeline
# ---------------------------
def main():
    cfg = load_cfg()
    jobs = filter_jobs(collect
