# core/emailer.py
import os, smtplib
from email.mime.text import MIMEText

def send_email(cfg, subject, body):
    cfg = cfg or {}
    eml = cfg.get("email", {})

    smtp_server = eml.get("smtp_server", "smtp.gmail.com")
    smtp_port = int(eml.get("smtp_port", 587))
    use_tls = bool(eml.get("use_tls", True))

    from_addr = eml.get("from") or os.getenv("GMAIL_USER")
    to_addr   = eml.get("to")   or os.getenv("GMAIL_TO") or os.getenv("GMAIL_USER")
    if not from_addr or not to_addr:
        raise RuntimeError("Missing email from/to. Add config.email or set GMAIL_USER/GMAIL_TO secrets.")

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr

    username = os.getenv("GMAIL_USER")
    password = os.getenv("GMAIL_PASS")
    if not (username and password):
        raise RuntimeError("Missing GMAIL_USER/GMAIL_PASS secrets for SMTP auth.")

    with smtplib.SMTP(smtp_server, smtp_port, timeout=30) as s:
        if use_tls:
            s.starttls()
        s.login(username, password)
        s.send_message(msg)
