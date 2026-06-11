from typing import Optional

from app.services.db import get_connection


class Contact:
    def __init__(self, id: int | None = None, name: str = "", email: str = "", notes: str = ""):
        self.id = id
        self.name = name
        self.email = email
        self.notes = notes

    @classmethod
    def from_row(cls, row) -> "Contact":
        return cls(id=row["id"], name=row["name"], email=row["email"], notes=row["notes"])

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name, "email": self.email, "notes": self.notes}

    def __repr__(self) -> str:
        return f"{self.name} <{self.email}>"


def add(name: str, email: str, notes: str = "") -> Contact:
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO contacts (name, email, notes) VALUES (?, ?, ?)",
        (name.strip(), email.strip(), notes.strip()),
    )
    conn.commit()
    return Contact(id=cursor.lastrowid, name=name.strip(), email=email.strip(), notes=notes.strip())


def find_by_name(name: str) -> Optional[Contact]:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM contacts WHERE LOWER(name) = LOWER(?)", (name.strip(),)
    ).fetchone()
    return Contact.from_row(row) if row else None


def find_by_email(email: str) -> Optional[Contact]:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM contacts WHERE LOWER(email) = LOWER(?)", (email.strip(),)
    ).fetchone()
    return Contact.from_row(row) if row else None


def search(query: str) -> list[Contact]:
    conn = get_connection()
    pattern = f"%{query.strip()}%"
    rows = conn.execute(
        "SELECT * FROM contacts WHERE name LIKE ? OR email LIKE ? ORDER BY name",
        (pattern, pattern),
    ).fetchall()
    return [Contact.from_row(r) for r in rows]


def list_all() -> list[Contact]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM contacts ORDER BY name").fetchall()
    return [Contact.from_row(r) for r in rows]


def delete(contact_id: int) -> bool:
    conn = get_connection()
    cursor = conn.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
    conn.commit()
    return cursor.rowcount > 0
