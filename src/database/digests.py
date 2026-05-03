import sqlite3
from datetime import datetime
from connection import get_connection


def save_digest(category, content):
    """Save a finished digest for a category. Returns the new digest id."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO digests (category, content, created_at) VALUES (?, ?, ?)",
            (category, content, now),
        )
        conn.commit()
        return cursor.lastrowid


def get_latest_digest(category):
    """Return the most recent digest for a category as a dict, or None."""
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            """
            SELECT id, category, content, created_at
            FROM digests
            WHERE category = ?
            ORDER BY created_at DESC, id DESC
            LIMIT 1
            """,
            (category,),
        ).fetchone()
    return dict(row) if row else None


def get_latest_unsent_summary():
    """Return the latest unsent summary as a dict, or None."""
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT id, title, content, created_at FROM summaries WHERE sent = 0 ORDER BY id DESC LIMIT 1"
        ).fetchone()
    return dict(row) if row else None


def get_latest_digests_for_categories(categories):
    """Return the latest digest per category for the given list of categories.

    Returns a dict mapping category -> digest dict. Categories without any
    digest are omitted.
    """
    result = {}
    for category in categories:
        digest = get_latest_digest(category)
        if digest is not None:
            result[category] = digest
    return result


def mark_summary_as_sent(summary_id):
    """Mark a summary as sent so it won't be sent again."""
    with get_connection() as conn:
        conn.execute(
            "UPDATE summaries SET sent = 1 WHERE id = ?",
            (summary_id,),
        )
        conn.commit()


