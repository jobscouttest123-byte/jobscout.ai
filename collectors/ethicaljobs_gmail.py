import re
import base64
from email import message_from_bytes
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# Regex to match EthicalJobs URLs
LINK_RE = re.compile(r"https://(www\.)?ethicaljobs\.com\.au/[^\s]+", re.I)

def fetch_ethicaljobs_from_gmail():
    """Fetch EthicalJobs links from Gmail inbox using Gmail API."""
    creds = Credentials.from_authorized_user_file("token.json", ["https://www.googleapis.com/auth/gmail.readonly"])
    service = build("gmail", "v1", credentials=creds)

    results = service.users().messages().list(userId="me", q="from:alerts@ethicaljobs.com.au").execute()
    messages = results.get("messages", [])

    jobs = []
    if not messages:
        return jobs

    for msg in messages[:10]:  # limit to latest 10
        msg_data = service.users().messages().get(userId="me", id=msg["id"], format="raw").execute()
        raw_msg = base64.urlsafe_b64decode(msg_data["raw"])
        email_msg = message_from_bytes(raw_msg)

        body = ""
        if email_msg.is_multipart():
            for part in email_msg.walk():
                if part.get_content_type() == "text/plain":
                    body += part.get_payload(decode=True).decode(errors="ignore")
        else:
            body = email_msg.get_payload(decode=True).decode(errors="ignore")

        for match in LINK_RE.findall(body):
            jobs.append(match)

    return jobs
