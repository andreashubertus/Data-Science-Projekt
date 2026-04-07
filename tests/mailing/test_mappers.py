import pytest

from mailing.mappers import MailingDataError, to_subscriber, to_summary


def test_to_subscriber_full():
    row = {
        "id": 1,
        "email": "test@example.com",
        "name": "Alice",
        "active": True
    }

    sub = to_subscriber(row)

    assert sub.id == 1
    assert sub.email == "test@example.com"
    assert sub.name == "Alice"
    assert sub.active is True


def test_to_subscriber_defaults():
    row = {
        "id": 2,
        "email": "test2@example.com"
    }

    sub = to_subscriber(row)

    assert sub.name is None
    assert sub.active is True


def test_to_subscriber_converts_zero_active_to_false():
    row = {
        "id": 3,
        "email": "test3@example.com",
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


def test_to_summary_full():
    row = {
        "id": 1,
        "title": "Title",
        "content": "Content",
        "created_at": "2026-03-29"
    }

    summary = to_summary(row)

    assert summary.id == 1
    assert summary.title == "Title"
    assert summary.content == "Content"
    assert summary.created_at == "2026-03-29"


def test_to_summary_without_created_at():
    row = {
        "id": 2,
        "title": "Title",
        "content": "Content"
    }

    summary = to_summary(row)

    assert summary.created_at is None


def test_to_summary_rejects_missing_content():
    row = {
        "id": 4,
        "title": "Title",
        "content": None
    }

    with pytest.raises(MailingDataError, match="content"):
        to_summary(row)


def test_to_summary_rejects_missing_title():
    row = {
        "id": 3,
        "title": None,
        "content": "Content"
    }

    with pytest.raises(MailingDataError, match="title"):
        to_summary(row)
