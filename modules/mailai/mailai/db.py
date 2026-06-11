from __future__ import annotations

import sqlite3
import threading
from pathlib import Path

from mailai.config import config

_local = threading.local()


def get_connection() -> sqlite3.Connection:
    if not hasattr(_local, "conn") or _local.conn is None:
        db_dir = Path(config.db_dir)
        db_dir.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(config.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        _local.conn = conn
        _migrate(conn)
    return _local.conn


def _migrate(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS contacts (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            email       TEXT    NOT NULL,
            notes       TEXT    DEFAULT '',
            created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
            updated_at  TEXT    NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS history (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            to_name     TEXT    DEFAULT '',
            to_email    TEXT    NOT NULL,
            subject     TEXT    DEFAULT '',
            body        TEXT    DEFAULT '',
            status      TEXT    NOT NULL CHECK(status IN ('sent','failed')),
            error       TEXT    DEFAULT NULL,
            created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
        );

        CREATE INDEX IF NOT EXISTS idx_contacts_name ON contacts(name);
        CREATE INDEX IF NOT EXISTS idx_history_created_at ON history(created_at);
    """)
    conn.commit()


def close() -> None:
    if hasattr(_local, "conn") and _local.conn is not None:
        _local.conn.close()
        _local.conn = None
