from typing import Any

from app.services.db import get_connection


def list_contacts(search: str | None = None) -> list[dict[str, Any]]:
    conn = get_connection()
    if search:
        rows = conn.execute(
            "SELECT * FROM contacts WHERE name LIKE ? OR phone LIKE ? ORDER BY name",
            (f"%{search}%", f"%{search}%"),
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM contacts ORDER BY name").fetchall()
    return [dict(r) for r in rows]


def get_contact(contact_id: int) -> dict[str, Any] | None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,)).fetchone()
    return dict(row) if row else None


def find_contact_by_phone(phone: str) -> dict[str, Any] | None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM contacts WHERE phone = ?", (phone,)).fetchone()
    return dict(row) if row else None


def create_contact(name: str, phone: str, notes: str = "") -> dict[str, Any]:
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO contacts (name, phone, notes) VALUES (?, ?, ?)",
        (name, phone, notes),
    )
    conn.commit()
    return get_contact(cur.lastrowid)


def update_contact(contact_id: int, name: str, phone: str, notes: str) -> dict[str, Any] | None:
    conn = get_connection()
    conn.execute(
        "UPDATE contacts SET name = ?, phone = ?, notes = ?, updated_at = datetime('now') WHERE id = ?",
        (name, phone, notes, contact_id),
    )
    conn.commit()
    return get_contact(contact_id)


def delete_contact(contact_id: int) -> bool:
    conn = get_connection()
    cur = conn.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
    conn.commit()
    return cur.rowcount > 0
