import sqlite3
from datetime import datetime
from src.database.connection import get_connection


def add_subscriber(email, name=None):
    """Add an email to the subscribers list. Returns True if added, False if already exists."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO subscribers (email, name, subscribed_at) VALUES (?, ?, ?)",
                (email, name, now),
            )
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def remove_subscriber(email):
    """Remove an email from the subscribers list. Returns True if removed, False if not found."""
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM subscribers WHERE email = ?", (email,))
        conn.commit()
    return cursor.rowcount > 0


def get_all_subscribers():
    """Return all subscriber emails as a list of strings."""
    with get_connection() as conn:
        rows = conn.execute("SELECT email FROM subscribers ORDER BY subscribed_at").fetchall()
    return [row[0] for row in rows]


def get_active_subscribers():
    """Return all active subscribers as a list of dicts."""
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT id, email, name, active FROM subscribers WHERE active = 1 ORDER BY subscribed_at"
        ).fetchall()
    return [dict(row) for row in rows]