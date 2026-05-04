import sqlite3
import pytest
from unittest.mock import patch
from src.database.connection import get_connection, init_db


def test_get_connection_returns_sqlite_connection():
    with patch("src.database.connection.DB_PATH", ":memory:"):
        conn = get_connection()
        assert isinstance(conn, sqlite3.Connection)
        conn.close()


def test_init_db_creates_tables():
    with patch("src.database.connection.DB_PATH", ":memory:"):
        # init_db opens its own connection, so we patch get_connection
        # to always return the same in-memory connection
        conn = sqlite3.connect(":memory:")
        with patch("src.database.connection.get_connection", return_value=conn):
            init_db()

        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        table_names = {row[0] for row in tables}

    expected = {"articles", "digests", "subscribers", "summaries", "delivery_results"}
    assert expected.issubset(table_names)
    conn.close()
