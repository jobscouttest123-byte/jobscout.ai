# core/filters.py
from datetime import datetime, timezone, timedelta

def _parse_date(dt):
    if not dt:
        return None
    if isinstance(dt, datetime):
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    s = str(dt).strip()
    try:
        # ISO with Z
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        return datetime.fromisoformat(s)
    except Exception:
        # Try common formats
        for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(s, fmt).replace(tzinfo=timezone.utc)
            except Exception:
                pass
    return None

def _recent_ok(job, cfg):
    days = (cfg.get("filters") or {}).get("recent_days")
    if not days:
        return True  # no recency constraint
    cutoff = datetime.now(timezone.utc) - timedelta(days=int(days))
    posted = job.get("posted_at")
    dt = _parse_date(posted)
    # If we can’t parse a date, exclude to honor “last 7 days”
    return (dt is not None) and (dt >= cutoff)

def _type_ok(job, cfg):
    et = (job.get("employment_type") or "").lower()
    allowed = [t.lower() for t in (cfg.get("allowed_types") or [])]
    return (not allowed) or (et == "" or et in allowed)

def _country_ok(job, cfg):
    country = (job.get("country") or "").upper()
    allowed = [c.upper() for c in (cfg.get("allowed_countries") or [])]
    return (not allowed) or (country == "" or country in allowed)

def _remote_ok(job, cfg):
    # When remote_only is False, we allow remote/hybrid/onsite
    f = (cfg.get("filters") or {})
    remote_only = bool(f.get("remote_only", False))
    if not remote_only:
        return True
    # If remote_only is True, accept jobs explicitly flagged remote
    return bool(job.get("remote", False))

def filter_jobs(jobs, cfg):
    cfg = cfg or {}
    out = []
    for j in jobs or []:
        if not _remote_ok(j, cfg):
            continue
        if not _type_ok(j, cfg):
            continue
        if not _country_ok(j, cfg):
            continue
        if not _recent_ok(j, cfg):
            continue
        out.append(j)
    return out
