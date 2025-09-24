# core/normalize.py
from datetime import datetime, timezone

def _bool_remote(v):
    if isinstance(v, bool):
        return v
    if v is None:
        return None
    s = str(v).strip().lower()
    if s in {"true", "yes", "y", "1", "remote", "fully remote", "anywhere"}:
        return True
    if s in {"false", "no", "n", "0", "onsite", "on-site"}:
        return False
    if "hybrid" in s:
        return None
    return None

def _work_mode(remote_flag, raw_remote_field):
    s = (str(raw_remote_field or "").strip().lower())
    if "hybrid" in s:
        return "hybrid"
    if remote_flag is True:
        return "remote"
    if remote_flag is False:
        return "onsite"
    return "unspecified"

def _pick_posted_at(job):
    for k in ("posted_at", "publication_date", "published_at", "created", "date"):
        if job.get(k):
            return job.get(k)
    return None

def normalize(job: dict, source: str) -> dict:
    job = job or {}
    title = job.get("title") or job.get("position") or job.get("role") or "Unspecified role"
    company = job.get("company") or job.get("company_name") or job.get("organization") or job.get("employer") or "Unknown"
    location = job.get("location") or job.get("city") or job.get("region") or "Remote"
    link = job.get("link") or job.get("url") or job.get("href") or ""

    remote_flag = _bool_remote(job.get("remote"))
    mode = _work_mode(remote_flag, job.get("remote") or job.get("work_mode") or job.get("job_type"))
    posted_at = _pick_posted_at(job)

    return {
        "title": title.strip() or "Unspecified role",
        "company": company.strip() or "Unknown",
        "location": location.strip() or "Remote",
        "link": link,
        "source": (source or "unknown").strip(),
        "remote": True if mode == "remote" else False if mode == "onsite" else None,
        "work_mode": mode,       # remote / hybrid / onsite / unspecified
        "posted_at": posted_at,  # string; filters.py parses it
        "llm_reasons": job.get("llm_reasons", []),
        "red_flags": job.get("red_flags", []),
        "must_ask": job.get("must_ask", []),
        "_raw": job,
    }
