import pytest

from src.mailing.content_builder import build_email
from src.mailing.models import Summary
from src.mailing.mappers import MailingDataError


def test_build_email_includes_title_and_content():
    summary = Summary(
        id=1,
        category="TECHNOLOGY",
        title="Test Title",
        content="Some content",
        created_at="2026-03-29"
    )

    email = build_email(summary)

    assert "TECHNOLOGY" in email.subject
    assert "TECHNOLOGY" in email.text_body
    assert "TECHNOLOGY" in email.html_body
    assert "Test Title" in email.subject
    assert "Some content" in email.text_body
    assert "Test Title" in email.html_body
    assert "Some content" in email.html_body


def test_build_email_with_date():
    summary = Summary(
        id=2,
        category="SPORTS",
        title="AI News",
        content="Important update",
        created_at="2026-03-29"
    )

    email = build_email(summary)

    assert "29.03" in email.subject
    assert "Date: 29.03" in email.text_body
    assert "29.03" in email.html_body


def test_build_email_without_date():
    summary = Summary(
        id=3,
        category="ECONOMY",
        title="No Date",
        content="Content",
        created_at=None
    )

    email = build_email(summary)

    assert "(" not in email.subject
    assert "Date:" not in email.text_body


def test_build_email_html_structure():
    summary = Summary(
        id=4,
        category="POLITICS",
        title="HTML Test",
        content="HTML content",
        created_at="2026-03-29"
    )

    email = build_email(summary)

    assert "<html>" in email.html_body
    assert "<body style=" in email.html_body
    assert "<h1 style=" in email.html_body
    assert "AI News Summary" in email.html_body
    assert "POLITICS" in email.html_body


def test_build_email_rejects_missing_content():
    summary = Summary(
        id=5,
        category="TECHNOLOGY",
        title="Broken",
        content=None,
        created_at="2026-03-29"
    )

    with pytest.raises(MailingDataError, match="content"):
        build_email(summary)


def test_build_email_rejects_missing_title():
    summary = Summary(
        id=6,
        category="SPORTS",
        title=None,
        content="Body",
        created_at="2026-03-29"
    )

    with pytest.raises(MailingDataError, match="title"):
        build_email(summary)


def test_build_email_rejects_missing_category():
    summary = Summary(
        id=7,
        category=None,
        title="Title",
        content="Body",
        created_at="2026-03-29"
    )

    with pytest.raises(MailingDataError, match="category"):
        build_email(summary)
