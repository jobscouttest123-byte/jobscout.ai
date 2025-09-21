import imaplib, email, re, os
from bs4 import BeautifulSoup

# Regex to match EthicalJobs links (raw string, all quotes properly escaped)
LINK_RE = re.compile("https://(?:www\.)?ethicaljobs\.com\.au/[^\s]+", re.I)

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

    # 1) Connect & login (IMAP is always on for personal Gmail)
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(user, pw)
    imap.select("INBOX")

    # 2) Search for alert emails (adjust if your sender is different)
    status, data = imap.search(None, 'FROM "alerts@ethicaljobs.com.au"')
    if status != "OK":
        print("[ethicaljobs_gmail] IMAP search failed")
        imap.logout()
        return jobs

    msg_nums = data[0].split()[-max_messages:]

    # 3) Parse each email and extract links from HTML body
    for num in msg_nums:
        status, msg_data = imap.fetch(num, "(RFC822)")
        if status != "OK":
            continue

        msg = email.message_from_bytes(msg_data[0][1])
        subject = msg.get("Subject", "EthicalJobs alert")

        # Prefer HTML body
        html = None
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/html":
                    html = part.get_payload(decode=True)
                    if html:
                        html = html.decode(part.get_content_charset() or "utf-8", errors="ignore")
                        break
        else:
            if msg.get_content_type() == "text/html":
                html = msg.get_payload(decode=True)
                if html:
                    html = html.decode(msg.get_content_charset() or "utf-8", errors="ignore")

        if not html:
            continue

        soup = BeautifulSoup(html, "html.parser")
        # Find all anchors and test hrefs against regex
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if LINK_RE.search(href):
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
