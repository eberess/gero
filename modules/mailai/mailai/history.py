from __future__ import annotations

from datetime import datetime
from typing import List

from mailai.db import get_connection


class HistoryEntry:
    def __init__(
        self,
        id: int | None = None,
        to_name: str = "",
        to_email: str = "",
        subject: str = "",
        body: str = "",
        status: str = "sent",
        error: str | None = None,
        created_at: str | None = None,
    ) -> None:
        self.id = id
        self.to_name = to_name
        self.to_email = to_email
        self.subject = subject
        self.body = body
        self.status = status
        self.error = error
        self.created_at = created_at or datetime.now().isoformat()

    @classmethod
    def from_row(cls, row) -> "HistoryEntry":
        return cls(
            id=row["id"],
            to_name=row["to_name"],
            to_email=row["to_email"],
            subject=row["subject"],
            body=row["body"],
            status=row["status"],
            error=row["error"],
            created_at=row["created_at"],
        )


def record_sent(to_name: str, to_email: str, subject: str, body: str) -> int:
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO history (to_name, to_email, subject, body, status) VALUES (?, ?, ?, ?, 'sent')",
        (to_name, to_email, subject, body),
    )
    conn.commit()
    return cursor.lastrowid


def record_failed(to_name: str, to_email: str, subject: str, body: str, error: str) -> int:
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO history (to_name, to_email, subject, body, status, error) VALUES (?, ?, ?, ?, 'failed', ?)",
        (to_name, to_email, subject, body, error),
    )
    conn.commit()
    return cursor.lastrowid


def list_recent(limit: int = 20) -> List[HistoryEntry]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM history ORDER BY created_at DESC LIMIT ?", (limit,)
    ).fetchall()
    return [HistoryEntry.from_row(r) for r in rows]
