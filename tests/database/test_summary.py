import sqlite3
import pytest
from unittest.mock import patch


def make_conn():
    conn = sqlite3.connect(":memory:")
    conn.execute("""
        CREATE TABLE summaries (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            category    TEXT NOT NULL,
            content     TEXT NOT NULL,
            created_at  TEXT
        )
    """)
    conn.commit()
    return conn


def test_save_chunk_inserts_row():
    conn = make_conn()
    with patch("src.database.summary.get_connection", return_value=conn):
        from src.database.summary import save_chunk
        row_id = save_chunk("tech", "summary text")

    assert isinstance(row_id, int)
    row = conn.execute("SELECT * FROM summaries WHERE id = ?", (row_id,)).fetchone()
    assert row is not None
    assert row[1] == "tech"
    assert row[2] == "summary text"


def test_save_chunk_returns_incrementing_ids():
    conn = make_conn()
    with patch("src.database.summary.get_connection", return_value=conn):
        from src.database.summary import save_chunk
        id1 = save_chunk("tech", "first")
        id2 = save_chunk("tech", "second")
    assert id2 > id1
