import sqlite3
import pytest
from unittest.mock import patch


def make_conn():
    conn = sqlite3.connect(":memory:")
    conn.execute("""
        CREATE TABLE subscribers (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            email         TEXT UNIQUE NOT NULL,
            name          TEXT,
            active        INTEGER NOT NULL DEFAULT 1,
            subscribed_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE subscriber_categories (
            subscriber_id INTEGER NOT NULL,
            category      TEXT NOT NULL,
            PRIMARY KEY (subscriber_id, category)
        )
    """)
    conn.commit()
    return conn


#add_subscriber

def test_add_subscriber_returns_true_on_success():
    conn = make_conn()
    with patch("src.database.subscriber.get_connection", return_value=conn):
        from src.database.subscriber import add_subscriber
        result = add_subscriber("user@example.com", "Alice", categories=["TECHNOLOGY", "SPORTS"])
    assert result is True
    categories = conn.execute(
        "SELECT category FROM subscriber_categories ORDER BY category"
    ).fetchall()
    assert [row[0] for row in categories] == ["SPORTS", "TECHNOLOGY"]


def test_add_subscriber_returns_false_on_duplicate():
    conn = make_conn()
    with patch("src.database.subscriber.get_connection", return_value=conn):
        from src.database.subscriber import add_subscriber
        add_subscriber("user@example.com")
        result = add_subscriber("user@example.com")
    assert result is False


#remove_subscriber

def test_remove_subscriber_returns_true_when_found():
    conn = make_conn()
    conn.execute(
        "INSERT INTO subscribers (email, subscribed_at) VALUES (?,?)",
        ("user@example.com", "2024-01-01 00:00:00"),
    )
    subscriber_id = conn.execute("SELECT id FROM subscribers WHERE email = ?", ("user@example.com",)).fetchone()[0]
    conn.execute(
        "INSERT INTO subscriber_categories (subscriber_id, category) VALUES (?,?)",
        (subscriber_id, "TECHNOLOGY"),
    )
    conn.commit()

    with patch("src.database.subscriber.get_connection", return_value=conn):
        from src.database.subscriber import remove_subscriber
        result = remove_subscriber("user@example.com")
    assert result is True
    rows = conn.execute("SELECT * FROM subscriber_categories").fetchall()
    assert rows == []


def test_remove_subscriber_returns_false_when_not_found():
    conn = make_conn()
    with patch("src.database.subscriber.get_connection", return_value=conn):
        from src.database.subscriber import remove_subscriber
        result = remove_subscriber("nobody@example.com")
    assert result is False


#get_all_subscribers

def test_get_all_subscribers_returns_email_list():
    conn = make_conn()
    conn.execute(
        "INSERT INTO subscribers (email, subscribed_at) VALUES (?,?)",
        ("a@example.com", "2024-01-01 00:00:00"),
    )
    conn.commit()

    with patch("src.database.subscriber.get_connection", return_value=conn):
        from src.database.subscriber import get_all_subscribers
        result = get_all_subscribers()
    assert result == ["a@example.com"]


#get_active_subscribers

def test_get_active_subscribers_excludes_inactive():
    conn = make_conn()
    conn.execute(
        "INSERT INTO subscribers (email, active, subscribed_at) VALUES (?,?,?)",
        ("active@example.com", 1, "2024-01-01 00:00:00"),
    )
    conn.execute(
        "INSERT INTO subscribers (email, active, subscribed_at) VALUES (?,?,?)",
        ("inactive@example.com", 0, "2024-01-01 00:00:00"),
    )
    conn.commit()

    with patch("src.database.subscriber.get_connection", return_value=conn):
        from src.database.subscriber import get_active_subscribers
        result = get_active_subscribers()

    emails = [r["email"] for r in result]
    assert "active@example.com" in emails
    assert "inactive@example.com" not in emails


def test_get_active_subscribers_filters_by_category():
    conn = make_conn()
    conn.execute(
        "INSERT INTO subscribers (email, active, subscribed_at) VALUES (?,?,?)",
        ("tech@example.com", 1, "2024-01-01 00:00:00"),
    )
    conn.execute(
        "INSERT INTO subscribers (email, active, subscribed_at) VALUES (?,?,?)",
        ("sports@example.com", 1, "2024-01-01 00:00:00"),
    )
    tech_id = conn.execute("SELECT id FROM subscribers WHERE email = ?", ("tech@example.com",)).fetchone()[0]
    sports_id = conn.execute("SELECT id FROM subscribers WHERE email = ?", ("sports@example.com",)).fetchone()[0]
    conn.execute(
        "INSERT INTO subscriber_categories (subscriber_id, category) VALUES (?,?)",
        (tech_id, "TECHNOLOGY"),
    )
    conn.execute(
        "INSERT INTO subscriber_categories (subscriber_id, category) VALUES (?,?)",
        (sports_id, "SPORTS"),
    )
    conn.commit()

    with patch("src.database.subscriber.get_connection", return_value=conn):
        from src.database.subscriber import get_active_subscribers
        result = get_active_subscribers("TECHNOLOGY")

    assert len(result) == 1
    assert result[0]["email"] == "tech@example.com"
    assert result[0]["category"] == "TECHNOLOGY"
