import sqlite3
from datetime import datetime


DB_PATH = "news.db"


def get_connection():
    """Opens and returns a connection to the SQLite database.

    Returns:
        A sqlite3.Connection object for DB_PATH.
    """
    return sqlite3.connect(DB_PATH)


def init_db():
    """Creates all required database tables if they do not exist.

    Creates the following tables:
        - articles: Scraped news articles with optional category.
        - digests: Generated digests per category with sent status.
        - subscribers: Email subscribers with active flag.
        - subscriber_categories: Many-to-many mapping of subscribers to categories.
        - summaries: Summary chunks generated per category.
        - delivery_results: Per-subscriber delivery outcomes linked
          to summaries and subscribers via foreign keys.
    """
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
                category    TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS digests (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                category    TEXT NOT NULL,
                content     TEXT NOT NULL,
                created_at  TEXT NOT NULL,
                sent        INTEGER NOT NULL DEFAULT 0
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
            CREATE TABLE IF NOT EXISTS subscriber_categories (
                subscriber_id INTEGER NOT NULL,
                category      TEXT NOT NULL,
                PRIMARY KEY (subscriber_id, category),
                FOREIGN KEY (subscriber_id) REFERENCES subscribers(id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS summaries (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                category    TEXT NOT NULL,
                content     TEXT NOT NULL,
                created_at  TEXT
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
