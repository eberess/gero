from typing import Any

from app.services.db import get_connection


def record_send(
    to_phone: str,
    message: str,
    to_name: str = "",
    gateway_id: str | None = None,
) -> int:
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO history (to_name, to_phone, message, gateway_id, status) VALUES (?, ?, ?, ?, 'sent')",
        (to_name, to_phone, message, gateway_id),
    )
    conn.commit()
    return cur.lastrowid


def record_failure(to_phone: str, message: str, error: str, to_name: str = "") -> int:
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO history (to_name, to_phone, message, status, error) VALUES (?, ?, ?, 'failed', ?)",
        (to_name, to_phone, message, error),
    )
    conn.commit()
    return cur.lastrowid


def list_history(
    limit: int = 50,
    offset: int = 0,
    status: str | None = None,
) -> list[dict[str, Any]]:
    conn = get_connection()
    if status:
        rows = conn.execute(
            "SELECT * FROM history WHERE status = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (status, limit, offset),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM history ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (limit, offset),
        ).fetchall()
    return [dict(r) for r in rows]


def get_history_entry(entry_id: int) -> dict[str, Any] | None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM history WHERE id = ?", (entry_id,)).fetchone()
    return dict(row) if row else None
