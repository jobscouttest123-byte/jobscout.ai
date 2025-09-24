# core/emailer.py
import smtplib
from email.message import EmailMessage

def send_email(cfg, subject, body):
    ecfg = cfg.get("email") or {}
    missing = [k for k in ["smtp_server", "smtp_port", "from", "to"] if k not in ecfg]
    if missing:
        raise ValueError(f"Email config missing keys: {missing}")

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = ecfg["from"]
    msg["To"] = ecfg["to"]
    msg.set_content(body)

    server = smtplib.SMTP(ecfg["smtp_server"], int(ecfg["smtp_port"]))
    if ecfg.get("use_tls", True):
        server.starttls()
    server.login(cfg.get("GMAIL_USER", ""), cfg.get("GMAIL_PASS", ""))
    server.send_message(msg)
    server.quit()
