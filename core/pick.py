def pick_top(jobs, n=3):
    ranked = sorted(
        jobs,
        key=lambda j: (-(j.get("llm_score") or 0), j.get("posted_at") or ""),
    )
    picked, seen = [], set()
    for j in ranked:
        key = (str(j.get("company")).lower(), str(j.get("title")).lower())
        if key in seen: 
            continue
        picked.append(j)
        seen.add(key)
        if len(picked) == n:
            break
    return picked
