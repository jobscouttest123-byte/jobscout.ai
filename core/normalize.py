def normalize(job, source):
    if source == "remotive":
        loc = (job or {}).get("candidate_required_location") or ""
        return {
            "source": "remotive",
            "title": job.get("title"),
            "company": job.get("company_name"),
            "location": loc,
            "country": "Remote",
            "remote": True,
            "employment_type": (job.get("job_type") or "").lower(),
            "salary_text": job.get("salary"),
            "salary_min": None,
            "salary_max": None,
            "currency": None,
            "link": job.get("url"),
            "description": job.get("description"),
            "posted_at": job.get("publication_date")
        }
    elif source == "adzuna":
        area = job.get("location", {}).get("area", [])
        country = (area[0] if area else "").upper()
        return {
            "source": "adzuna",
            "title": job.get("title"),
            "company": job.get("company", {}).get("display_name"),
            "location": job.get("location", {}).get("display_name"),
            "country": country,
            "remote": "remote" in (job.get("description","").lower()),
            "employment_type": (job.get("contract_type") or "").lower(),
            "salary_text": None,
            "salary_min": job.get("salary_min"),
            "salary_max": job.get("salary_max"),
            "currency": job.get("salary_currency"),
            "link": job.get("redirect_url"),
            "description": job.get("description"),
            "posted_at": job.get("created")
        }
    else:
        return None
