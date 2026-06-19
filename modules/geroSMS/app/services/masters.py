from typing import Any

from app.services.db import get_connection


def list_masters(active_only: bool = False) -> list[dict[str, Any]]:
    conn = get_connection()
    if active_only:
        rows = conn.execute("SELECT * FROM masters WHERE active = 1 ORDER BY name").fetchall()
    else:
        rows = conn.execute("SELECT * FROM masters ORDER BY name").fetchall()
    return [dict(r) for r in rows]


def get_master(master_id: int) -> dict[str, Any] | None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM masters WHERE id = ?", (master_id,)).fetchone()
    return dict(row) if row else None


def get_master_by_phone(phone: str) -> dict[str, Any] | None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM masters WHERE phone = ?", (phone,)).fetchone()
    return dict(row) if row else None


def create_master(name: str, phone: str, notes: str = "") -> dict[str, Any]:
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO masters (name, phone, notes) VALUES (?, ?, ?)",
        (name, phone, notes),
    )
    conn.commit()
    return get_master(cur.lastrowid)


def update_master(master_id: int, name: str, phone: str, notes: str, active: bool) -> dict[str, Any] | None:
    conn = get_connection()
    conn.execute(
        "UPDATE masters SET name = ?, phone = ?, notes = ?, active = ?, updated_at = datetime('now') WHERE id = ?",
        (name, phone, notes, int(active), master_id),
    )
    conn.commit()
    return get_master(master_id)


def delete_master(master_id: int) -> bool:
    conn = get_connection()
    cur = conn.execute("DELETE FROM masters WHERE id = ?", (master_id,))
    conn.commit()
    return cur.rowcount > 0
