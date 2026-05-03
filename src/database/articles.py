import sqlite3
from datetime import datetime
from connection import get_connection

def insert_articles(articles):
    """
    Insert a list of articles into the database.
    Each article is expected to be in Andi's format:
        [headline, link, date, text, scraped_at]
    Skips duplicates (same link).
    Returns the number of newly inserted articles.
    """
    inserted = 0
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with get_connection() as conn:
        for article in articles:
            if article is None:
                continue
            headline, link, date, text, scraped_at = article
            try:
                conn.execute(
                    """
                    INSERT INTO articles (headline, link, date, text, scraped_at, inserted_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (headline, link, date, text, scraped_at, now),
                )
                inserted += 1
            except sqlite3.IntegrityError:
                # Duplicate link — skip
                pass
        conn.commit()

    return inserted


def get_all_articles():
    """Return all articles as a list of dicts."""
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM articles ORDER BY inserted_at DESC"
        ).fetchall()
    return [dict(row) for row in rows]