import email
import imaplib
from email.header import decode_header
from typing import Optional

from app.dependencies import mail_config


class EmailMessage:
    def __init__(self, uid: int, subject: str = "", sender: str = "",
                 recipient: str = "", date: str = "", body_text: str = "", body_html: str = ""):
        self.uid = uid
        self.subject = subject
        self.sender = sender
        self.recipient = recipient
        self.date = date
        self.body_text = body_text
        self.body_html = body_html

    def to_dict(self) -> dict:
        return {"uid": self.uid, "subject": self.subject, "sender": self.sender,
                "recipient": self.recipient, "date": self.date,
                "body_text": self.body_text[:500] if self.body_text else ""}


def _decode_str(value: str | None) -> str:
    if not value:
        return ""
    decoded_parts = decode_header(value)
    result = []
    for part, charset in decoded_parts:
        if isinstance(part, bytes):
            try:
                result.append(part.decode(charset or "utf-8", errors="replace"))
            except LookupError:
                result.append(part.decode("utf-8", errors="replace"))
        else:
            result.append(str(part))
    return "".join(result)


def _connect(folder: str = "INBOX") -> imaplib.IMAP4_SSL:
    conn = imaplib.IMAP4_SSL(mail_config.imap_server, mail_config.imap_port)
    conn.login(mail_config.imap_username, mail_config.imap_password)
    conn.select(folder)
    return conn


def _parse_email(raw_email: bytes, uid: int) -> EmailMessage:
    msg = email.message_from_bytes(raw_email)
    subject = _decode_str(msg.get("Subject", ""))
    sender = _decode_str(msg.get("From", ""))
    recipient = _decode_str(msg.get("To", ""))
    date = _decode_str(msg.get("Date", ""))
    body_text = ""
    body_html = ""

    if msg.is_multipart():
        for part in msg.walk():
            ct = part.get_content_type()
            if ct == "text/plain" and not body_text:
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or "utf-8"
                    try:
                        body_text = payload.decode(charset, errors="replace")
                    except LookupError:
                        body_text = payload.decode("utf-8", errors="replace")
            elif ct == "text/html" and not body_html:
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or "utf-8"
                    try:
                        body_html = payload.decode(charset, errors="replace")
                    except LookupError:
                        body_html = payload.decode("utf-8", errors="replace")
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            charset = msg.get_content_charset() or "utf-8"
            try:
                body_text = payload.decode(charset, errors="replace")
            except LookupError:
                body_text = payload.decode("utf-8", errors="replace")

    return EmailMessage(uid=uid, subject=subject, sender=sender,
                        recipient=recipient, date=date,
                        body_text=body_text, body_html=body_html)


def list_inbox(limit: int = 10) -> list[EmailMessage]:
    conn = _connect("INBOX")
    try:
        _, data = conn.search(None, "ALL")
        uids = data[0].split() if data[0] else []
        uids = uids[-limit:] if len(uids) > limit else uids
        messages = []
        for uid in reversed(uids):
            _, data = conn.fetch(uid, "(RFC822)")
            if data and data[0]:
                raw_email = data[0][1]
                messages.append(_parse_email(raw_email, int(uid)))
        return messages
    finally:
        conn.close()
        conn.logout()


def read_email(uid: int, folder: str = "INBOX") -> Optional[EmailMessage]:
    conn = imaplib.IMAP4_SSL(mail_config.imap_server, mail_config.imap_port)
    conn.login(mail_config.imap_username, mail_config.imap_password)
    try:
        actual = folder
        if folder.lower() == "sent":
            actual = _get_sent_folder(conn)
        conn.select(actual)
        _, data = conn.fetch(str(uid).encode(), "(RFC822)")
        if data and data[0]:
            raw_email = data[0][1]
            return _parse_email(raw_email, uid)
        return None
    finally:
        try:
            conn.close()
        except Exception:
            pass
        conn.logout()


def _get_sent_folder(conn: imaplib.IMAP4_SSL) -> str:
    status, data = conn.list()
    if status == "OK":
        for folder_data in data:
            if not folder_data:
                continue
            folder_str = folder_data.decode("utf-8", errors="ignore")
            if "\\Sent" in folder_str:
                parts = folder_str.split(' "/" ')
                if len(parts) > 1:
                    return parts[-1]
    return "Sent"


def list_sent(limit: int = 10) -> list[EmailMessage]:
    conn = imaplib.IMAP4_SSL(mail_config.imap_server, mail_config.imap_port)
    conn.login(mail_config.imap_username, mail_config.imap_password)
    try:
        sent_folder = _get_sent_folder(conn)
        conn.select(sent_folder)
        _, data = conn.search(None, "ALL")
        uids = data[0].split() if data[0] else []
        uids = uids[-limit:] if len(uids) > limit else uids
        messages = []
        for uid in reversed(uids):
            _, data = conn.fetch(uid, "(RFC822)")
            if data and data[0]:
                raw_email = data[0][1]
                messages.append(_parse_email(raw_email, int(uid)))
        return messages
    finally:
        try:
            conn.close()
        except Exception:
            pass
        conn.logout()


def append_sent(msg: str) -> None:
    conn = imaplib.IMAP4_SSL(mail_config.imap_server, mail_config.imap_port)
    conn.login(mail_config.imap_username, mail_config.imap_password)
    try:
        sent_folder = _get_sent_folder(conn)
        conn.append(sent_folder, None, None, msg.encode("utf-8"))
    finally:
        try:
            conn.close()
        except Exception:
            pass
        conn.logout()
