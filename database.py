import sqlite3
from datetime import datetime


DB_PATH = "news.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                headline    TEXT NOT NULL,
                link        TEXT UNIQUE NOT NULL,
                date        TEXT,
                text        TEXT,
                scraped_at  TEXT,
                inserted_at TEXT NOT NULL,
                summary     TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS subscribers (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                email        TEXT UNIQUE NOT NULL,
                subscribed_at TEXT NOT NULL
            )
        """)
        conn.commit()


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


def get_unsummarized_articles():
    """Return articles that have not been summarized yet (for the LLM stage)."""
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM articles WHERE summary IS NULL ORDER BY inserted_at DESC"
        ).fetchall()
    return [dict(row) for row in rows]


def add_subscriber(email):
    """Add an email to the subscribers list. Returns True if added, False if already exists."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO subscribers (email, subscribed_at) VALUES (?, ?)",
                (email, now),
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


if __name__ == "__main__":
    from scraper import scrape_tagesschau

    init_db()
    print("Scraping articles...")
    articles = scrape_tagesschau()
    count = insert_articles(articles)
    print(f"{count} neue Artikel in die Datenbank eingefügt.")
