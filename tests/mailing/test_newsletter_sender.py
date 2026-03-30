from mailing.newsletter_sender import send_latest_newsletter

class DBConnectionMock:
    def __init__(self):
        self.saved_results = []
        self.marked_summary_ids = []

    def get_latest_unsent_summary(self):
        return {
            "id": 1,
            "title": "AI Breakthrough in 2026",
            "content": "Researchers developed a new model that significantly improves reasoning tasks.",
            "created_at": "2026-03-29",
        }

    def get_active_subscribers(self):
        return [
            {
                "id": 1,
                "email": "user1@example.com",
                "name": "Alice",
                "active": True,
            },
            {
                "id": 2,
                "email": "user2@example.com",
                "name": "Bob",
                "active": True,
            },
        ]

    def save_delivery_result(self, summary_id, subscriber_id, success, error_message):
        self.saved_results.append(
            {
                "summary_id": summary_id,
                "subscriber_id": subscriber_id,
                "success": success,
                "error_message": error_message,
            }
        )

    def mark_summary_as_sent(self, summary_id):
        self.marked_summary_ids.append(summary_id)


def test_send_latest_newsletter_returns_result_for_each_subscriber():
    db_handler = DBConnectionMock()

    results = send_latest_newsletter(db_handler)

    assert len(results) == 2
    assert all(result.success is True for result in results)


def test_send_latest_newsletter_saves_each_delivery_result():
    db_handler = DBConnectionMock()

    send_latest_newsletter(db_handler)

    assert len(db_handler.saved_results) == 2
    assert db_handler.saved_results[0]["summary_id"] == 1
    assert db_handler.saved_results[0]["subscriber_id"] == 1
    assert db_handler.saved_results[1]["subscriber_id"] == 2


def test_send_latest_newsletter_marks_summary_as_sent_once():
    db_handler = DBConnectionMock()

    send_latest_newsletter(db_handler)

    assert db_handler.marked_summary_ids == [1]