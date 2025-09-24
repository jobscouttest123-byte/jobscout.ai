# core/emailer.py
import os
import smtplib
from email.mime.text import MIMEText

def send_email(cfg, subject, body):
    cfg = cfg or {}
    eml = cfg.get("email", {})  # yaml section for from/to/host/port/tls

    smtp_server = eml.get("smtp_server", "smtp.gmail.com")
    smtp_port   = int(eml.get("smtp_port", 587))
    use_tls     = bool(eml.get("use_tls", True))

    # Always send from the authenticated Gmail to avoid Gmail rejections
    from_addr = eml.get("from") or os.getenv("GMAIL_USER")
    to_addr   = eml.get("to")   or os.getenv("GMAIL_TO") or os.getenv("GMAIL_USER")
    if not from_addr or not to_addr:
        raise RuntimeError("Missing from/to: set config.email.from/to or GMAIL_USER/GMAIL_TO secrets.")

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr

    # *** Use GitHub Secrets (environment) for auth, not YAML ***
    username = os.getenv("GMAIL_USER")
    password = os.getenv("GMAIL_PASS")
    if not username or not password:
        raise RuntimeError("Missing GMAIL_USER or GMAIL_PASS secrets.")

    with smtplib.SMTP(smtp_server, smtp_port, timeout=30) as s:
        if use_tls:
            s.starttls()
        s.login(username, password)
        s.send_message(msg)
