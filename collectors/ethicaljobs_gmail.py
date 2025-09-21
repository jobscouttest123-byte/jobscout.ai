import imaplib, email, re, os
from bs4 import BeautifulSoup

# Match EthicalJobs job links
LINK_RE = re.compile(r"https?://(?:www\.)?ethicaljobs\.com\.au/[^\s\"'>]+", re.I)

def fetch_ethicaljobs_from_gmail(max_messages=30):
    """Fetch EthicalJobs links from Gmail using IMAP + App Password."""
    jobs = []
    user = os.getenv("GMAIL_USER")
    pw = os.getenv("GMAIL_PASS")
    if not user or not pw:
        return jobs

    # 1) Connect to Gmail IMAP
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(user, pw)
    imap.select("INBOX")

    # 2) Search for EthicalJobs alert emails
    status, data = imap.search(None, 'FROM "alerts@ethicaljobs.com.au"')
    if status != "OK":
        imap.logout()
        return jobs

    # 3) Read latest messages (limit for speed)
    for num in data[0].split()[-max_messages:]:
        status, msg_data = imap.fetch(num, "(RFC822)")
        if status != "OK":
            continue

        msg = email.message_from_bytes(msg_data[0][1])

        # Prefer HTML body for links
        body_html = None
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/html":
                    body_html = part.get_payload(decode=True).decode(
                        part.get_content_charset() or "utf-8", errors="ignore"
                    )
                    break
        else:
            if msg.get_content_type() == "text/html":
                body_html = msg.get_payload(decode=True).decode(
                    msg.get_content_charset() or "utf-8", errors="ignore"
                )

        # 4) Extract EthicalJobs links
        if body_html:
            soup = BeautifulSoup(body_html, "html.parser")
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if LINK_RE.search(href):
                    jobs.append({
                        "source": "ethicaljobs_gmail",
                        "title": msg.get("Subject", "EthicalJobs listing"),
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
                        "description": "Discovered via EthicalJobs Gmail alert",
                        "posted_at": None
                    })

    # 5) Cleanup
    imap.close()
    imap.logout()
    return jobs
