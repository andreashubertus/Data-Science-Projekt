import sqlite3
import pytest
from unittest.mock import patch


def make_conn():
    conn = sqlite3.connect(":memory:")
    conn.execute("""
        CREATE TABLE digests (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            category    TEXT NOT NULL,
            content     TEXT NOT NULL,
            created_at  TEXT NOT NULL,
            sent        INTEGER NOT NULL DEFAULT 0
        )
    """)
    conn.commit()
    return conn


#save_digest

def test_save_digest_inserts_row():
    conn = make_conn()
    with patch("src.database.digests.get_connection", return_value=conn):
        from src.database.digests import save_digest
        save_digest("tech", "digest content")

    row = conn.execute("SELECT * FROM digests").fetchone()
    assert row is not None
    assert row[1] == "tech"
    assert row[2] == "digest content"
    assert row[4] == 0  # sent = 0


#get_latest_unsent_digest
def test_get_latest_unsent_digest_returns_dict():
    conn = make_conn()
    conn.execute(
        "INSERT INTO digests (category, content, created_at, sent) VALUES (?,?,?,?)",
        ("tech", "content", "2024-01-01 00:00:00", 0),
    )
    conn.commit()

    with patch("src.database.digests.get_connection", return_value=conn):
        from src.database.digests import get_latest_unsent_digest
        result = get_latest_unsent_digest("tech")

    assert result is not None
    assert result["category"] == "tech"
    assert result["content"] == "content"


def test_get_latest_unsent_digest_returns_none_when_all_sent():
    conn = make_conn()
    conn.execute(
        "INSERT INTO digests (category, content, created_at, sent) VALUES (?,?,?,?)",
        ("tech", "content", "2024-01-01 00:00:00", 1),
    )
    conn.commit()

    with patch("src.database.digests.get_connection", return_value=conn):
        from src.database.digests import get_latest_unsent_digest
        result = get_latest_unsent_digest("tech")

    assert result is None


#mark_digest_as_sent

def test_mark_digest_as_sent_updates_flag():
    conn = make_conn()
    conn.execute(
        "INSERT INTO digests (category, content, created_at, sent) VALUES (?,?,?,?)",
        ("tech", "content", "2024-01-01 00:00:00", 0),
    )
    conn.commit()
    digest_id = conn.execute("SELECT id FROM digests").fetchone()[0]

    with patch("src.database.digests.get_connection", return_value=conn):
        from src.database.digests import mark_digest_as_sent
        mark_digest_as_sent(digest_id)

    sent = conn.execute("SELECT sent FROM digests WHERE id = ?", (digest_id,)).fetchone()[0]
    assert sent == 1
