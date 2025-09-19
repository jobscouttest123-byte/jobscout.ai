import os, smtplib
from email.mime.text import MIMEText

def send_email(cfg, subject, body):
    smtp_server = cfg['email']['smtp_server']
    smtp_port = cfg['email']['smtp_port']
    username = os.getenv("GMAIL_USER", cfg['email']['username'])
    password = os.getenv("GMAIL_PASS", cfg['email']['password'])
    to_email = cfg['email']['to']

    msg = MIMEText(body, "plain")
    msg["Subject"] = subject
    msg["From"] = username
    msg["To"] = to_email

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(username, password)
        server.send_message(msg)
