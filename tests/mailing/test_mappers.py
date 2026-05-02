import pytest

from src.mailing.mappers import MailingDataError, to_subscriber, to_summary


def test_to_subscriber_full():
    row = {
        "id": 1,
        "email": "test@example.com",
        "category": "TECHNOLOGY",
        "name": "Alice",
        "active": True
    }

    sub = to_subscriber(row)

    assert sub.id == 1
    assert sub.email == "test@example.com"
    assert sub.category == "TECHNOLOGY"
    assert sub.name == "Alice"
    assert sub.active is True


def test_to_subscriber_defaults():
    row = {
        "id": 2,
        "email": "test2@example.com",
        "category": "SPORTS"
    }

    sub = to_subscriber(row)

    assert sub.category == "SPORTS"
    assert sub.name is None
    assert sub.active is True


def test_to_subscriber_converts_zero_active_to_false():
    row = {
        "id": 3,
        "email": "test3@example.com",
        "category": "ECONOMY",
        "active": 0
    }

    sub = to_subscriber(row)

    assert sub.active is False


def test_to_subscriber_rejects_missing_email():
    row = {
        "id": 4,
        "email": None
    }

    with pytest.raises(MailingDataError, match="email"):
        to_subscriber(row)


def test_to_subscriber_rejects_missing_category():
    row = {
        "id": 5,
        "email": "test5@example.com",
        "category": None
    }

    with pytest.raises(MailingDataError, match="category"):
        to_subscriber(row)


def test_to_summary_full():
    row = {
        "id": 1,
        "category": "TECHNOLOGY",
        "title": "Title",
        "content": "Content",
        "created_at": "2026-03-29"
    }

    summary = to_summary(row)

    assert summary.id == 1
    assert summary.category == "TECHNOLOGY"
    assert summary.title == "Title"
    assert summary.content == "Content"
    assert summary.created_at == "2026-03-29"


def test_to_summary_without_created_at():
    row = {
        "id": 2,
        "category": "SPORTS",
        "title": "Title",
        "content": "Content"
    }

    summary = to_summary(row)

    assert summary.category == "SPORTS"
    assert summary.created_at is None


def test_to_summary_rejects_missing_content():
    row = {
        "id": 4,
        "category": "ECONOMY",
        "title": "Title",
        "content": None
    }

    with pytest.raises(MailingDataError, match="content"):
        to_summary(row)


def test_to_summary_rejects_missing_title():
    row = {
        "id": 3,
        "category": "POLITICS",
        "title": None,
        "content": "Content"
    }

    with pytest.raises(MailingDataError, match="title"):
        to_summary(row)


def test_to_summary_rejects_missing_category():
    row = {
        "id": 5,
        "category": None,
        "title": "Title",
        "content": "Content"
    }

    with pytest.raises(MailingDataError, match="category"):
        to_summary(row)
