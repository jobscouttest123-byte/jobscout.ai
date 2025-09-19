import imaplib, email, re, os
from bs4 import BeautifulSoup

LINK_RE = re.compile(r"https?://(?:www\.)?ethicaljobs\.com\.au/[^"'\s>]+", re.I)

def fetch_ethicaljobs_from_gmail(max_messages=30):
    jobs = []
    user = os.getenv("GMAIL_USER")
    pw = os.getenv("GMAIL_PASS")
    if not user or not pw:
        return jobs

    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(user, pw)
    imap.select("inbox")
    status, data = imap.search(None, 'FROM "alerts@ethicaljobs.com.au"')
    if status != "OK":
        imap.logout()
        return jobs

    for num in data[0].split()[-max_messages:]:
        status, msg_data = imap.fetch(num, "(RFC822)")
        if status != "OK":
            continue
        msg = email.message_from_bytes(msg_data[0][1])
        subj = msg.get("Subject", "EthicalJobs listing")
        body_html = ""
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                try:
                    body_html = part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8", errors="ignore")
                except Exception:
                    body_html = ""
                break
        links = []
        if body_html:
            soup = BeautifulSoup(body_html, "html.parser")
            links = [a["href"] for a in soup.find_all("a", href=True) if LINK_RE.search(a["href"])]
        for link in links:
            jobs.append({
                "source": "ethicaljobs_gmail",
                "title": subj,
                "company": None,
                "location": None,
                "country": "AU",
                "remote": None,
                "employment_type": None,
                "salary_text": None,
                "salary_min": None,
                "salary_max": None,
                "currency": None,
                "link": link,
                "description": "Discovered via EthicalJobs Gmail alert",
                "posted_at": None
            })
    imap.close()
    imap.logout()
    return jobs
