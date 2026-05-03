import sqlite3
from datetime import datetime
from src.database.connection import get_connection
from src.llm.classifier import classify_article

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


def transfer_article_categories():
    """Classify all articles without a category and write the result back to the DB.

    Fetches every article where ``category`` is NULL, calls ``classify_article``
    on its text, and updates the row in place. Articles without text are skipped.

    Returns:
        Tuple (updated, skipped) with the counts of processed and skipped articles.
    """
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT id, text FROM articles WHERE category IS NULL"
        ).fetchall()

    updated = 0
    skipped = 0

    for row in rows:
        article_id = row["id"]
        text = row["text"]

        if not text or not text.strip():
            skipped += 1
            continue

        try:
            category = classify_article(text)
        except Exception as exc:
            print(f"Could not classify article {article_id}: {exc}")
            skipped += 1
            continue

        with get_connection() as conn:
            conn.execute(
                "UPDATE articles SET category = ? WHERE id = ?",
                (category, article_id),
            )
            conn.commit()

        updated += 1

    print(f"transfer_article_categories: {updated} updated, {skipped} skipped.")
    return updated, skipped

def get_articles_by_category(category):
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM articles WHERE category = ? ORDER BY inserted_at DESC",
            (category,),
        ).fetchall()
    return [dict(row) for row in rows]