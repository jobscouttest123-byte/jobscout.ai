import requests
def fetch_remotive():
    url = "https://remotive.com/api/remote-jobs"
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        return r.json().get("jobs", [])
    except Exception:
        return []
