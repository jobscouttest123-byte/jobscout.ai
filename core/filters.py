# core/filters.py
from datetime import datetime, timezone, timedelta

def _parse_date(dt):
    if not dt:
        return None
    if isinstance(dt, datetime):
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    s = str(dt).strip()
    try:
        # ISO 8601 with optional Z
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        return datetime.fromisoformat(s)
    except Exception:
        for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(s, fmt).replace(tzinfo=timezone.utc)
            except Exception:
                pass
    return None

def _recent_ok(job, cfg):
    days = (cfg.get("filters") or {}).get("recent_days")
    if not days:
        return True
    cutoff = datetime.now(timezone.utc) - timedelta(days=int(days))
    dt = _parse_date(job.get("posted_at"))
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
    print(f"[filters] {len(out)}/{len(jobs or [])} jobs kept after filtering")
    return out
