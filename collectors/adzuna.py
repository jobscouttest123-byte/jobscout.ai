import os, requests
ADZUNA_APP_ID = os.getenv("ADZUNA_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_KEY")
def fetch_adzuna(country="au", results=20):
    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        return []
    url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1"
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "results_per_page": results,
        "what": "UX OR Experience Designer OR Service Designer OR Product Designer OR Customer Experience",
        "content_type": "json",
        "max_days_old": 10
    }
    try:
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        return r.json().get("results", [])
    except Exception:
        return []
