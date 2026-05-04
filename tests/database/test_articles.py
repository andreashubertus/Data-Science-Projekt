import sqlite3
import pytest
from unittest.mock import patch, MagicMock


def make_conn():
    """Return an in-memory SQLite connection with the articles table."""
    conn = sqlite3.connect(":memory:")
    conn.execute("""
        CREATE TABLE articles (
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
    conn.commit()
    return conn


SAMPLE = ("Headline", "http://example.com", "2024-01-01", "Body text", "2024-01-01 10:00:00")

#insert_articles

def test_insert_articles_inserts_successfully():
    conn = make_conn()
    with patch("src.database.articles.get_connection", return_value=conn):
        from src.database.articles import insert_articles
        count = insert_articles([SAMPLE])
    assert count == 1

 
def test_insert_articles_skips_none():
    conn = make_conn()
    with patch("src.database.articles.get_connection", return_value=conn):
        from src.database.articles import insert_articles
        count = insert_articles([None, SAMPLE])
    assert count == 1


def test_insert_articles_skips_duplicates():
    conn = make_conn()
    with patch("src.database.articles.get_connection", return_value=conn):
        from src.database.articles import insert_articles
        insert_articles([SAMPLE])
        count = insert_articles([SAMPLE])
    assert count == 0


#get_all_articles

def test_get_all_articles_returns_list_of_dicts():
    conn = make_conn()
    conn.execute(
        "INSERT INTO articles (headline, link, date, text, scraped_at, inserted_at) VALUES (?,?,?,?,?,?)",
        ("H", "http://a.com", None, None, None, "2024-01-01 00:00:00"),
    )
    conn.commit()
    with patch("src.database.articles.get_connection", return_value=conn):
        from src.database.articles import get_all_articles
        rows = get_all_articles()
    assert isinstance(rows, list)
    assert rows[0]["headline"] == "H"


#transfer_article_categories

def test_transfer_article_categories_updates_category():
    conn = make_conn()
    conn.execute(
        "INSERT INTO articles (headline, link, inserted_at, text) VALUES (?,?,?,?)",
        ("H", "http://b.com", "2024-01-01 00:00:00", "Some text"),
    )
    conn.commit()

    with patch("src.database.articles.get_connection", return_value=conn):
        from src.database.articles import transfer_article_categories
        updated, skipped = transfer_article_categories(classify_fn=lambda text: "tech")

    assert updated == 1
    assert skipped == 0


def test_transfer_article_categories_skips_empty_text():
    conn = make_conn()
    conn.execute(
        "INSERT INTO articles (headline, link, inserted_at, text) VALUES (?,?,?,?)",
        ("H", "http://c.com", "2024-01-01 00:00:00", ""),
    )
    conn.commit()

    with patch("src.database.articles.get_connection", return_value=conn):
        from src.database.articles import transfer_article_categories
        updated, skipped = transfer_article_categories(classify_fn=lambda text: "tech")

    assert updated == 0
    assert skipped == 1


def test_transfer_article_categories_skips_on_exception():
    conn = make_conn()
    conn.execute(
        "INSERT INTO articles (headline, link, inserted_at, text) VALUES (?,?,?,?)",
        ("H", "http://f.com", "2024-01-01 00:00:00", "Some text"),
    )
    conn.commit()

    def failing_classify(text):
        raise Exception("fail")

    with patch("src.database.articles.get_connection", return_value=conn):
        from src.database.articles import transfer_article_categories
        updated, skipped = transfer_article_categories(classify_fn=failing_classify)

    assert updated == 0
    assert skipped == 1


#get_articles_by_category

def test_get_articles_by_category_filters_correctly():
    conn = make_conn()
    conn.execute(
        "INSERT INTO articles (headline, link, inserted_at, category) VALUES (?,?,?,?)",
        ("H1", "http://d.com", "2024-01-01 00:00:00", "tech"),
    )
    conn.execute(
        "INSERT INTO articles (headline, link, inserted_at, category) VALUES (?,?,?,?)",
        ("H2", "http://e.com", "2024-01-01 00:00:00", "sports"),
    )
    conn.commit()

    with patch("src.database.articles.get_connection", return_value=conn):
        from src.database.articles import get_articles_by_category
        rows = get_articles_by_category("tech")

    assert len(rows) == 1
    assert rows[0]["headline"] == "H1"
