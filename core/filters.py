# core/filters.py
from datetime import datetime, timezone, timedelta

def _parse_date(dt):
    """
    Parse many date formats and ALWAYS return a timezone-aware (UTC) datetime.
    Returns None when unparsable.
    """
    if not dt:
        return None
    if isinstance(dt, datetime):
        # force aware (UTC) if naive
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)

    s = str(dt).strip()
    try:
        # Handle trailing Z (UTC)
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        d = datetime.fromisoformat(s)
        # force aware (UTC) if naive
        return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
    except Exception:
        pass

    # Common fallbacks (force UTC tzinfo)
    for fmt in ("%Y-%m-%d",
                "%Y/%m/%d",
                "%d-%m-%Y",
                "%Y-%m-%d %H:%M:%S",
                "%Y/%m/%d %H:%M:%S"):
        try:
            return datetime.strptime(s, fmt).replace(tzinfo=timezone.utc)
        except Exception:
            continue

    return None

def _recent_ok(job, cfg):
    days = (cfg.get("filters") or {}).get("recent_days")
    if not days:
        return True  # no recency constraint
    cutoff = datetime.now(timezone.utc) - timedelta(days=int(days))
    dt = _parse_date(job.get("posted_at"))
    # Exclude if unparsable (to honor "last N days" strictly)
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
    # If remote_only is False, allow all (remote, hybrid, onsite)
    remote_only = bool((cfg.get("filters") or {}).get("remote_only", False))
    if not remote_only:
        return True
    return bool(job.get("remote", False))
    
def _exclude_keywords(job, cfg):
    title = (job.get("title") or "").lower()
    excluded = [(k or "").lower() for k in ((cfg.get("filters") or {}).get("exclude_keywords") or [])]
    return not any(k in title for k in excluded)

def filter_jobs(jobs, cfg):
    cfg = cfg or {}
    fcfg = (cfg.get("filters") or {})
    remote_only = bool(fcfg.get("remote_only", False))

    out = []
    for j in jobs or []:
        if remote_only and not j.get("remote", False):
            continue
        if not _type_ok(j, cfg):
            continue
        if not _country_ok(j, cfg):
            continue
        if not _recent_ok(j, cfg):
            continue
        if not _exclude_keywords(j, cfg):   # ✅ new exclusion check
            continue
        out.append(j)
    print(f"[filters] {len(out)}/{len(jobs or [])} jobs kept after filtering")
    return out
