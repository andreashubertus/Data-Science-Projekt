import sqlite3
from datetime import datetime
from src.database.connection import get_connection


def save_digest(category, content):
    """Inserts a finished digest for a category into the digests table.

    Args:
        category: Category name as str the digest belongs to.
        content: Digest content as str to be stored.
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO digests (category, content, created_at) VALUES (?, ?, ?)",
            (category, content, now),
        )
        conn.commit()


def get_latest_unsent_digest(category):
    """Returns the most recent unsent digest for a given category.

    Args:
        category: Category name as str to filter by.

    Returns:
        Dict with keys id, category, content, and created_at,
        or None if no unsent digest exists for the category.
    """
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            """
            SELECT id, category, content, created_at
            FROM digests
            WHERE sent = 0 AND category = ?
            ORDER BY created_at DESC, id DESC
            LIMIT 1
            """,
            (category,),
        ).fetchone()
    return dict(row) if row else None


def mark_digest_as_sent(digest_id):
    """Marks a digest as sent to prevent it from being sent again.

    Args:
        digest_id: Primary key of the digest row as int.
    """
    with get_connection() as conn:
        conn.execute(
            "UPDATE digests SET sent = 1 WHERE id = ?",
            (digest_id,),
        )
        conn.commit()
