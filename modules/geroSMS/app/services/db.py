import sqlite3
import threading
from pathlib import Path

from app.dependencies import sms_config

_local = threading.local()


def get_connection() -> sqlite3.Connection:
    if not hasattr(_local, "conn") or _local.conn is None:
        db_dir = Path(sms_config.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(sms_config.db_path)
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
            phone       TEXT    NOT NULL,
            notes       TEXT    DEFAULT '',
            created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
            updated_at  TEXT    NOT NULL DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS history (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            to_name         TEXT    DEFAULT '',
            to_phone        TEXT    NOT NULL,
            message         TEXT    DEFAULT '',
            gateway_id      TEXT    DEFAULT NULL,
            status          TEXT    NOT NULL DEFAULT 'pending',
            error           TEXT    DEFAULT NULL,
            created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_contacts_phone ON contacts(phone);
        CREATE INDEX IF NOT EXISTS idx_contacts_name ON contacts(name);
        CREATE INDEX IF NOT EXISTS idx_history_created_at ON history(created_at);
        CREATE INDEX IF NOT EXISTS idx_history_status ON history(status);
        CREATE TABLE IF NOT EXISTS masters (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            phone       TEXT    NOT NULL UNIQUE,
            notes       TEXT    DEFAULT '',
            active      INTEGER NOT NULL DEFAULT 1,
            created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
            updated_at  TEXT    NOT NULL DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_masters_phone ON masters(phone);
    """)
    conn.commit()


def close() -> None:
    if hasattr(_local, "conn") and _local.conn is not None:
        _local.conn.close()
        _local.conn = None
