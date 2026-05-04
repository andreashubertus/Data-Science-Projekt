import sqlite3
from datetime import datetime
from .connection import get_connection


def save_chunk(category, summarytext):
    """Inserts a summary chunk for a category into the summaries table.

    Args:
        category: Category name as str the summary belongs to.
        summarytext: Summary content as str to be stored.

    Returns:
        Row id of the newly inserted record as int.
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO summaries (category, content, created_at) VALUES (?, ?, ?)",
            (category, summarytext, now),
        )
        conn.commit()
        return cursor.lastrowid
