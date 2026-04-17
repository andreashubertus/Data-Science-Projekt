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
                name         TEXT,
                active       INTEGER NOT NULL DEFAULT 1,
                subscribed_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS summaries (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT NOT NULL,
                content     TEXT NOT NULL,
                created_at  TEXT,
                sent        INTEGER NOT NULL DEFAULT 0
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS delivery_results (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                summary_id      INTEGER NOT NULL,
                subscriber_id   INTEGER NOT NULL,
                success         INTEGER NOT NULL,
                error_message   TEXT,
                delivered_at    TEXT NOT NULL,
                FOREIGN KEY (summary_id) REFERENCES summaries(id),
                FOREIGN KEY (subscriber_id) REFERENCES subscribers(id)
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


def update_summary(article_id, summary):
    """Update the summary for a given article by its ID."""
    with get_connection() as conn:
        conn.execute(
            "UPDATE articles SET summary = ? WHERE id = ?",
            (summary, article_id),
        )
        conn.commit()


def add_subscriber(email, name=None):
    """Add an email to the subscribers list. Returns True if added, False if already exists."""
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


# ── Mailing-Funktionen (für Vitalii) ──────────────────────────────────


def get_latest_unsent_summary():
    """Return the oldest unsent summary as a dict, or None."""
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT id, title, content, created_at FROM summaries WHERE sent = 0 ORDER BY id ASC LIMIT 1"
        ).fetchone()
    return dict(row) if row else None


def get_active_subscribers():
    """Return all active subscribers as a list of dicts."""
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT id, email, name, active FROM subscribers WHERE active = 1 ORDER BY subscribed_at"
        ).fetchall()
    return [dict(row) for row in rows]


def save_delivery_result(summary_id, subscriber_id, success, error_message=None):
    """Save one delivery result for a subscriber."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO delivery_results (summary_id, subscriber_id, success, error_message, delivered_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (summary_id, subscriber_id, int(success), error_message, now),
        )
        conn.commit()


def mark_summary_as_sent(summary_id):
    """Mark a summary as sent so it won't be sent again."""
    with get_connection() as conn:
        conn.execute(
            "UPDATE summaries SET sent = 1 WHERE id = ?",
            (summary_id,),
        )
        conn.commit()


if __name__ == "__main__":
    from scraper import scrape_tagesschau

    init_db()
    print("Scraping articles...")
    articles = scrape_tagesschau()
    count = insert_articles(articles)
    print(f"{count} neue Artikel in die Datenbank eingefügt.")
