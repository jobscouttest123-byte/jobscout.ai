import imaplib, email, re, os
from bs4 import BeautifulSoup

# Regex to match EthicalJobs links (raw string, all quotes properly escaped)
LINK_RE = re.compile(r"https?://(?:www\.)?ethicaljobs\.com\.au/[^\s\"'<>]+", re.I)

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
