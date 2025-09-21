import imaplib, email, os
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def _is_ethicaljobs_link(href: str) -> bool:
    if not href or not href.startswith("http"):
        return False
    # normalize and check domain
    try:
        netloc = urlparse(href).netloc.lower()
        path = urlparse(href).path or ""
    except Exception:
        return False
    # accept ethicaljobs.com.au with or without www
    if netloc.endswith("ethicaljobs.com.au") and path.strip("/") != "":
        return True
    return False

def fetch_ethicaljobs_from_gmail(max_messages=40):
    """
    Fetch EthicalJobs links from Gmail using IMAP + App Password.
    Requires env: GMAIL_USER, GMAIL_PASS
    """
    user = os.getenv("GMAIL_USER")
    pw = os.getenv("GMAIL_PASS")
    jobs = []

    if not user or not pw:
        print("[ethicaljobs_gmail] Missing GMAIL_USER/GMAIL_PASS")
        return jobs

    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(user, pw)
    imap.select("INBOX")

    # adjust the FROM if your alerts sender differs
    status, data = imap.search(None, 'FROM "alerts@ethicaljobs.com.au"')
    if status != "OK":
        print("[ethicaljobs_gmail] IMAP search failed")
        imap.logout()
        return jobs

    msg_nums = data[0].split()[-max_messages:]

    for num in msg_nums:
        status, msg_data = imap.fetch(num, "(RFC822)")
        if status != "OK":
            continue

        msg = email.message_from_bytes(msg_data[0][1])
        subject = msg.get("Subject", "EthicalJobs alert")

        html = None
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/html":
                    raw = part.get_payload(decode=True)
                    if raw:
                        html = raw.decode(part.get_content_charset() or "utf-8", errors="ignore")
                        break
        else:
            if msg.get_content_type() == "text/html":
                raw = msg.get_payload(decode=True)
                if raw:
                    html = raw.decode(msg.get_content_charset() or "utf-8", errors="ignore")

        if not html:
            continue

        soup = BeautifulSoup(html, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if _is_ethicaljobs_link(href):
                jobs.append({
                    "source": "ethicaljobs_gmail",
                    "title": subject,
                    "company": None,
                    "location": None,
                    "country": "AU",
                    "remote": None,
                    "employment_type": None,
                    "salary_text": None,
                    "salary_min": None,
                    "salary_max": None,
                    "currency": None,
                    "link": href,
                    "description": "Link extracted from EthicalJobs alert email",
                    "posted_at": None
                })

    imap.close()
    imap.logout()
    print(f"[ethicaljobs_gmail] Collected {len(jobs)} links")
    return jobs
