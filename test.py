from mailing.newsletter_sender import send_latest_newsletter


class DBConnectionMock:

    def get_latest_unsent_summary(self):
        return {
        "id": 1,
        "title": "AI Breakthrough in 2026",
        "content": "Researchers developed a new model that significantly improves reasoning tasks.",
        "created_at": "2026-03-29"
    }

    def get_active_subscribers(self):
        """
    Temporary mock function for testing.
    Returns a list of subscribers in the expected DB format.
    """
        return [
        {
            "id": 1,
            "email": "user1@example.com",
            "name": "Alice",
            "active": True
        },
        {
            "id": 2,
            "email": "user2@example.com",
            "name": "Bob",
            "active": True
        }
    ]

    def save_delivery_result(self, summary_id, subscriber_id, success, error_message):
        print(
            f"Mock save_delivery_result(summary_id={summary_id}, subscriber_id={subscriber_id}, "
            f"success={success}, error_message={error_message})"
        )

    def mark_summary_as_sent(self, summary_id):
        print(f"Mock mark_summary_as_sent(summary_id={summary_id})")

def main():
    send_latest_newsletter(DBConnectionMock())

if __name__ == "__main__":
    main()