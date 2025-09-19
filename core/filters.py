def _meets_salary_floor(job, cfg):
    et = (job.get("employment_type") or "").lower()
    if "contract" in et and (job.get("salary_min") or job.get("salary_max")):
        return True
    if job.get("country") == "AU" and job.get("salary_min"):
        return job["salary_min"] >= cfg["salary_floor"]["au_yearly_gross"]
    if job.get("country") == "UK" and job.get("salary_min"):
        return job["salary_min"] >= cfg["salary_floor"]["uk_yearly_gross"]
    return True

def _type_ok(job, cfg):
    et = (job.get("employment_type") or "").lower()
    return (not et) or any(et == t.lower() for t in cfg["allowed_types"])

def _geo_ok(job, cfg):
    if job.get("remote") and cfg.get("accept_remote", True):
        return True
    c = job.get("country")
    return (not c) or (c in cfg.get("allowed_countries", []))

def filter_jobs(jobs, cfg):
    out = []
    for j in jobs:
        if not _geo_ok(j, cfg): 
            continue
        if not _type_ok(j, cfg):
            continue
        if not _meets_salary_floor(j, cfg):
            continue
        out.append(j)
    return out
