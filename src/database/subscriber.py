import sqlite3
from datetime import datetime
from src.database.connection import get_connection


def add_subscriber(email, name=None):
    """Adds an email address to the subscribers list.

    Args:
        email: Email address as str to subscribe.
        name: Optional display name as str. Defaults to None.

    Returns:
        True if the subscriber was added, False if the email
        already exists.
    """
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
    """Removes an email address from the subscribers list.

    Args:
        email: Email address as str to remove.

    Returns:
        True if the subscriber was removed, False if the email
        was not found.
    """
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM subscribers WHERE email = ?", (email,))
        conn.commit()
    return cursor.rowcount > 0


def get_all_subscribers():
    """Returns all subscriber email addresses.

    Returns:
        List of email address strings, ordered by subscribed_at.
    """
    with get_connection() as conn:
        rows = conn.execute("SELECT email FROM subscribers ORDER BY subscribed_at").fetchall()
    return [row[0] for row in rows]


def get_active_subscribers():
    """Returns all active subscribers.

    Returns:
        List of dicts with keys id, email, name, and active,
        ordered by subscribed_at.
    """
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT id, email, name, active FROM subscribers WHERE active = 1 ORDER BY subscribed_at"
        ).fetchall()
    return [dict(row) for row in rows]