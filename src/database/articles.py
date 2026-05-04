import sqlite3
from datetime import datetime
from .connection import get_connection

def insert_articles(articles):
    """Inserts a list of articles into the database.

    Skips None entries and duplicates identified by link.

    Args:
        articles: List of tuples of the form
            (headline, link, date, text, scraped_at).
            None entries in the list are ignored.

    Returns:
        Number of successfully inserted articles as int.
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
    """Returns all articles from the database, sorted descending.

    Returns:
        List of dicts, each containing all columns of one article.
        Sorted by inserted_at (newest first).
    """
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM articles ORDER BY inserted_at DESC"
        ).fetchall()
    return [dict(row) for row in rows]


def transfer_article_categories(classify_fn):
    """Classifies uncategorized articles and persists the category.

    Fetches all articles without a category, calls classify_fn()
    for each, and writes the result back. Articles with empty text or
    classification errors are skipped.

    Args:
        classify_fn: Callable that accepts an article text as str
            and returns a category name as str.

    Returns:
        Tuple (updated, skipped) with the count of updated and
        skipped articles respectively.
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
            category = classify_fn(text)
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
    """Returns all articles belonging to a given category.

    Args:
        category: Category name as str to filter by.

    Returns:
        List of dicts with all columns of matching articles,
        sorted by inserted_at (newest first).
    """
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM articles WHERE category = ? ORDER BY inserted_at DESC",
            (category,),
        ).fetchall()
    return [dict(row) for row in rows]
