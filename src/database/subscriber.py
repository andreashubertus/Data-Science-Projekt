import sqlite3
from datetime import datetime
from .connection import get_connection


def add_subscriber(email, name=None, categories=None):
    """Adds an email address to the subscribers list.

    Args:
        email: Email address as str to subscribe.
        name: Optional display name as str. Defaults to None.
        categories: Optional iterable of category names.

    Returns:
        True if the subscriber was added, False if the email
        already exists.
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    categories = sorted(set(categories or []))
    try:
        with get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO subscribers (email, name, subscribed_at) VALUES (?, ?, ?)",
                (email, name, now),
            )
            subscriber_id = cursor.lastrowid
            for category in categories:
                conn.execute(
                    """
                    INSERT INTO subscriber_categories (subscriber_id, category)
                    VALUES (?, ?)
                    """,
                    (subscriber_id, category),
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
        row = conn.execute(
            "SELECT id FROM subscribers WHERE email = ?",
            (email,),
        ).fetchone()
        if row is None:
            return False

        subscriber_id = row[0]
        conn.execute(
            "DELETE FROM subscriber_categories WHERE subscriber_id = ?",
            (subscriber_id,),
        )
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


def get_active_subscribers(category=None):
    """Returns all active subscribers.

    Returns:
        List of dicts with keys id, email, name, active, and
        optionally category if a category filter is used.
    """
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        if category is None:
            rows = conn.execute(
                "SELECT id, email, name, active FROM subscribers WHERE active = 1 ORDER BY subscribed_at"
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT s.id, s.email, s.name, s.active, sc.category
                FROM subscribers s
                JOIN subscriber_categories sc ON sc.subscriber_id = s.id
                WHERE s.active = 1 AND sc.category = ?
                ORDER BY s.subscribed_at
                """,
                (category,),
            ).fetchall()
    return [dict(row) for row in rows]
