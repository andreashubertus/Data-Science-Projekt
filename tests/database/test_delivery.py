import sqlite3
import pytest
from unittest.mock import patch


def make_conn():
    conn = sqlite3.connect(":memory:")
    conn.execute("""
        CREATE TABLE delivery_results (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            summary_id      INTEGER NOT NULL,
            subscriber_id   INTEGER NOT NULL,
            success         INTEGER NOT NULL,
            error_message   TEXT,
            delivered_at    TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn


def test_save_delivery_result_success():
    conn = make_conn()
    with patch("src.database.delivery.get_connection", return_value=conn):
        from src.database.delivery import save_delivery_result
        save_delivery_result(summary_id=1, subscriber_id=2, success=True)

    row = conn.execute("SELECT * FROM delivery_results").fetchone()
    assert row is not None
    assert row[1] == 1       # summary_id
    assert row[2] == 2       # subscriber_id
    assert row[3] == 1       # success = True → 1
    assert row[4] is None    # no error message


def test_save_delivery_result_failure_stores_error():
    conn = make_conn()
    with patch("src.database.delivery.get_connection", return_value=conn):
        from src.database.delivery import save_delivery_result
        save_delivery_result(summary_id=1, subscriber_id=3, success=False, error_message="SMTP error")

    row = conn.execute("SELECT * FROM delivery_results").fetchone()
    assert row[3] == 0               # success = False → 0
    assert row[4] == "SMTP error"
