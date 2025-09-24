# core/normalize.py

def _bool_remote(v):
    # Normalize various remote flags/strings to bool
    if isinstance(v, bool):
        return v
    if v is None:
        return True  # assume remote if missing (safe default for your use case)
    s = str(v).strip().lower()
    return s in {"true", "yes", "y", "1", "remote", "fully remote", "anywhere"}

def normalize(job: dict, source: str) -> dict:
    """
    Return a unified job dict with safe defaults so the email never shows 'None'.
    Fields your pipeline expects:
      title, company, location, link, source, remote, value_match, red_flags, questions
    """
    job = job or {}

    # Common incoming keys to map from (rss/remotive/adzuna etc.)
    title = job.get("title") or job.get("position") or job.get("role") or ""
    company = job.get("company") or job.get("organization") or job.get("employer") or "Unknown"
    location = job.get("location") or job.get("city") or job.get("region") or "Remote"

    # Some sources use 'url', others 'link'
    link = job.get("link") or job.get("url") or job.get("href") or ""

    # Normalize remote to a bool
    remote = _bool_remote(job.get("remote"))

    return {
        "title": title.strip() or "Unspecified role",
        "company": company.strip() or "Unknown",
        "location": location.strip() or "Remote",
        "link": link,
        "source": (source or "unknown").strip(),
        "remote": remote,
        # Optional enriched fields (may be added by scorer)
        "value_match": job.get("value_match", ""),
        "red_flags": job.get("red_flags", ""),
        "questions": job.get("questions", ""),
        # Keep original for debugging (optional)
        "_raw": job,
    }
