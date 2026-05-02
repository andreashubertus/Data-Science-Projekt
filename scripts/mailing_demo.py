from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.mailing.newsletter_sender import send_latest_newsletter


class DBConnectionMock:
    def get_latest_unsent_summary(self):
        return {
            "id": 1,
            "category": "TECHNOLOGY",
            "title": "AI Breakthroughs and Market Moves",
            "content": (
                "Researchers presented a new AI model that shows stronger reasoning performance in multi-step tasks "
                "and benchmark evaluations.\n\n"
                "At the same time, several companies announced new AI tools for business workflows, with a strong "
                "focus on automation, document analysis, and internal knowledge search.\n\n"
                "The market reaction was also notable: technology stocks connected to AI infrastructure and cloud "
                "services saw renewed investor attention after the announcements.\n\n"
                "Overall, today's developments suggest that AI is continuing to move from experimental use cases "
                "toward broader adoption in real products and business processes."
            ),
            "created_at": "2026-03-29"
        }

    def get_active_subscribers(self, category):
        """Return mock subscribers for the requested category."""
        return [
            {
                "id": 1,
                "email": "ai.news.summarizer.dhbw@gmail.com",
                "category": category,
                "name": "Vitalii",
                "active": True
            },
            {
                "id": 2,
                "email": "user2@example.com",
                "category": category,
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
    results = send_latest_newsletter(DBConnectionMock())

    print("\nDelivery results:")
    for result in results:
        print(
            f"- subscriber_email={result.subscriber_email}, "
            f"success={result.success}, error_message={result.error_message}"
        )


if __name__ == "__main__":
    main()
