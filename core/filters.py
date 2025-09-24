# core/filters.py
def _type_ok(job, cfg):
    et = (job.get("employment_type") or "").lower()
    allowed = [t.lower() for t in (cfg.get("allowed_types") or [])]
    # If no allowed_types configured, don't block on type
    return (not allowed) or (et == "" or et in allowed)

def _country_ok(job, cfg):
    country = (job.get("country") or "").upper()
    allowed = [c.upper() for c in (cfg.get("allowed_countries") or [])]
    # If no allowed_countries configured, don't block on country
    return (not allowed) or (country == "" or country in allowed)

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
        out.append(j)
    return out
