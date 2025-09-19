import feedparser
from datetime import datetime
def fetch_from_feeds(feed_urls, source_label="rss"):
    jobs = []
    for url in feed_urls:
        try:
            feed = feedparser.parse(url)
            for e in feed.entries:
                jobs.append({
                    "source": source_label,
                    "title": e.get("title"),
                    "company": None,
                    "location": None,
                    "country": None,
                    "remote": None,
                    "employment_type": None,
                    "salary_text": None,
                    "salary_min": None,
                    "salary_max": None,
                    "currency": None,
                    "link": e.get("link"),
                    "description": e.get("summary", "") or e.get("description", ""),
                    "posted_at": e.get("published", e.get("updated", "")) or datetime.utcnow().isoformat(),
                })
        except Exception:
            continue
    return jobs
