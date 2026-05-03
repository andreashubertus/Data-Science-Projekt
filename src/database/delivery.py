from datetime import datetime
from src.database.connection import get_connection


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





