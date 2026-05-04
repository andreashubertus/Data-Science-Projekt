from datetime import datetime
from .connection import get_connection


def save_delivery_result(summary_id, subscriber_id, success, error_message=None):
    """Inserts a delivery result for a single subscriber into the database.

    Args:
        summary_id: Primary key of the related summary row as int.
        subscriber_id: Primary key of the subscriber row as int.
        success: Whether the delivery succeeded as bool.
        error_message: Optional error description as str if the
            delivery failed. Defaults to None.
    """
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




