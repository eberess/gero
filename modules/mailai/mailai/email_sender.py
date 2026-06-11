from __future__ import annotations

import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from mailai.config import config
from mailai.imap_client import append_sent


def send(
    to_email: str,
    subject: str,
    body: str,
    to_name: str = "",
    from_email: Optional[str] = None,
    from_name: Optional[str] = None,
    timeout: int = 30,
) -> None:
    from_email = from_email or config.smtp_from_email
    from_name = from_name or config.smtp_from_name or from_email

    msg = MIMEMultipart("alternative")
    msg["From"] = f"{from_name} <{from_email}>"
    msg["To"] = f"{to_name} <{to_email}>" if to_name else to_email
    msg["Subject"] = subject

    html_body = body.replace("\n", "<br>\n")
    html = f"""<html><body><p>{html_body}</p></body></html>"""

    msg.attach(MIMEText(body, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))

    context = ssl.create_default_context()

    port = config.smtp_port

    if port == 587:
        with smtplib.SMTP(config.smtp_server, port, timeout=timeout) as server:
            server.starttls(context=context)
            server.login(config.smtp_username, config.smtp_password)
            server.sendmail(from_email, [to_email], msg.as_string())
    else:
        with smtplib.SMTP_SSL(
            config.smtp_server, port, timeout=timeout, context=context
        ) as server:
            server.login(config.smtp_username, config.smtp_password)
            server.sendmail(from_email, [to_email], msg.as_string())

    try:
        append_sent(msg.as_string())
    except Exception:
        pass
