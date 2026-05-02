from unittest.mock import patch

import pytest

from src.mailing.newsletter_sender import send_latest_newsletter
from src.mailing.mappers import MailingDataError

class DBConnectionMock:
    def __init__(self):
        self.saved_results = []
        self.marked_summary_ids = []

    def get_latest_unsent_summary(self):
        return {
            "id": 1,
            "category": "TECHNOLOGY",
            "title": "AI Breakthrough in 2026",
            "content": "Researchers developed a new model that significantly improves reasoning tasks.",
            "created_at": "2026-03-29",
        }

    def get_active_subscribers(self, category):
        assert category == "TECHNOLOGY"
        return [
            {
                "id": 1,
                "email": "user1@example.com",
                "category": "TECHNOLOGY",
                "name": "Alice",
                "active": True,
            },
            {
                "id": 2,
                "email": "user2@example.com",
                "category": "TECHNOLOGY",
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


def test_send_latest_newsletter_returns_one_result_per_subscriber():
    db_handler = DBConnectionMock()

    with patch("src.mailing.newsletter_sender.send_email") as mock_send_email:
        mock_send_email.side_effect = [
            type("Result", (), {"success": True, "error_message": None})(),
            type("Result", (), {"success": True, "error_message": None})(),
        ]
        results = send_latest_newsletter(db_handler)

    assert len(results) == 2


def test_send_latest_newsletter_returns_success_for_valid_subscribers():
    db_handler = DBConnectionMock()

    with patch("src.mailing.newsletter_sender.send_email") as mock_send_email:
        mock_send_email.side_effect = [
            type("Result", (), {"success": True, "error_message": None})(),
            type("Result", (), {"success": True, "error_message": None})(),
        ]
        results = send_latest_newsletter(db_handler)

    assert all(result.success is True for result in results)


def test_send_latest_newsletter_saves_each_delivery_result():
    db_handler = DBConnectionMock()

    with patch("src.mailing.newsletter_sender.send_email") as mock_send_email:
        mock_send_email.side_effect = [
            type("Result", (), {"success": True, "error_message": None})(),
            type("Result", (), {"success": True, "error_message": None})(),
        ]
        send_latest_newsletter(db_handler)

    assert len(db_handler.saved_results) == 2
    assert db_handler.saved_results[0]["summary_id"] == 1
    assert db_handler.saved_results[0]["subscriber_id"] == 1
    assert db_handler.saved_results[1]["subscriber_id"] == 2


def test_send_latest_newsletter_sends_only_to_matching_category_subscribers():
    db_handler = DBConnectionMock()

    with patch("src.mailing.newsletter_sender.send_email") as mock_send_email:
        mock_send_email.side_effect = [
            type("Result", (), {"success": True, "error_message": None})(),
            type("Result", (), {"success": True, "error_message": None})(),
        ]
        results = send_latest_newsletter(db_handler)

    assert len(results) == 2
    assert all(saved_result["summary_id"] == 1 for saved_result in db_handler.saved_results)


def test_send_latest_newsletter_marks_summary_as_sent_once():
    db_handler = DBConnectionMock()

    with patch("src.mailing.newsletter_sender.send_email") as mock_send_email:
        mock_send_email.side_effect = [
            type("Result", (), {"success": True, "error_message": None})(),
            type("Result", (), {"success": True, "error_message": None})(),
        ]
        send_latest_newsletter(db_handler)

    assert db_handler.marked_summary_ids == [1]


def test_send_latest_newsletter_returns_empty_list_when_no_summary():
    class NoSummaryDB(DBConnectionMock):
        def get_latest_unsent_summary(self):
            return None

    results = send_latest_newsletter(NoSummaryDB())

    assert results == []


def test_send_latest_newsletter_does_not_mark_summary_when_no_summary_exists():
    class NoSummaryDB(DBConnectionMock):
        def get_latest_unsent_summary(self):
            return None

    db_handler = NoSummaryDB()

    send_latest_newsletter(db_handler)

    assert db_handler.marked_summary_ids == []


def test_send_latest_newsletter_returns_empty_list_when_no_subscribers():
    class NoSubscribersDB(DBConnectionMock):
        def get_active_subscribers(self, category):
            return []

    results = send_latest_newsletter(NoSubscribersDB())

    assert results == []


def test_send_latest_newsletter_does_not_mark_summary_when_no_subscribers_exist():
    class NoSubscribersDB(DBConnectionMock):
        def get_active_subscribers(self, category):
            return []

    db_handler = NoSubscribersDB()

    send_latest_newsletter(db_handler)

    assert db_handler.marked_summary_ids == []


def test_send_latest_newsletter_raises_on_invalid_subscriber_data():
    class InvalidSubscriberDB(DBConnectionMock):
        def get_active_subscribers(self, category):
            return [
                {
                    "id": 1,
                    "email": None,
                    "category": "TECHNOLOGY",
                    "name": "Alice",
                    "active": True,
                }
            ]

    with pytest.raises(MailingDataError, match="email"):
        send_latest_newsletter(InvalidSubscriberDB())


def test_send_latest_newsletter_raises_on_category_mismatch():
    class WrongCategoryDB(DBConnectionMock):
        def get_active_subscribers(self, category):
            return [
                {
                    "id": 1,
                    "email": "user1@example.com",
                    "category": "SPORTS",
                    "name": "Alice",
                    "active": True,
                }
            ]

    with pytest.raises(MailingDataError, match="does not match"):
        send_latest_newsletter(WrongCategoryDB())
