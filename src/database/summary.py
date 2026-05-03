import sqlite3
from datetime import datetime
from src.database.connection import get_connection


def save_chunk(category, summarytext):
    """Save a summary chunk for a category into the summaries table. Returns the new row id."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO summaries (category, content, created_at) VALUES (?, ?, ?)",
            (category, summarytext, now),
        )
        conn.commit()
        return cursor.lastrowid


def get_latest_unsent_summary():
    """Return the latest unsent summary as a dict, or None."""
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT id, title, content, created_at FROM summaries WHERE sent = 0 ORDER BY id DESC LIMIT 1"
        ).fetchone()
    return dict(row) if row else None


def mark_summary_as_sent(summary_id):
    """Mark a summary as sent so it won't be sent again."""
    with get_connection() as conn:
        conn.execute(
            "UPDATE summaries SET sent = 1 WHERE id = ?",
            (summary_id,),
        )
        conn.commit()