import json
import smtplib
from email.mime.text import MIMEText
import requests
from typing import Optional
from app.core.config import settings


def send_slack(text: str) -> bool:
    url = settings.alerts_slack_webhook
    if not url:
        return False
    try:
        resp = requests.post(url, json={"text": text}, timeout=5)
        return resp.status_code in (200, 204)
    except Exception:
        return False


def send_email(subject: str, body: str) -> bool:
    host = settings.alerts_email_smtp_host
    user = settings.alerts_email_username
    pwd = settings.alerts_email_password
    from_addr = settings.alerts_email_from
    to_addr = settings.alerts_email_to
    if not all([host, user, pwd, from_addr, to_addr]):
        return False
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_addr
    msg['To'] = to_addr
    try:
        with smtplib.SMTP(host, settings.alerts_email_smtp_port) as s:
            s.starttls()
            s.login(user, pwd)
            s.sendmail(from_addr, [to_addr], msg.as_string())
        return True
    except Exception:
        return False


def notify_flow(flow_summary: str):
    sent = False
    sent |= send_slack(flow_summary)
    sent |= send_email("Flow Alert", flow_summary)
    return sent
