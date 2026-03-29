

from mailing.content_builder import build_email
from mailing.models import Summary


def test_build_email_basic():
    summary = Summary(
        id=1,
        title="Test Title",
        content="Some content",
        created_at="2026-03-29"
    )

    email = build_email(summary)

    assert "Test Title" in email.subject
    assert "Some content" in email.text_body
    assert "Test Title" in email.html_body
    assert "Some content" in email.html_body


def test_build_email_with_date():
    summary = Summary(
        id=2,
        title="AI News",
        content="Important update",
        created_at="2026-03-29"
    )

    email = build_email(summary)

    assert "29.03" in email.subject


def test_build_email_without_date():
    summary = Summary(
        id=3,
        title="No Date",
        content="Content",
        created_at=None
    )

    email = build_email(summary)

    assert "(" not in email.subject


def test_build_email_html_structure():
    summary = Summary(
        id=4,
        title="HTML Test",
        content="HTML content",
        created_at="2026-03-29"
    )

    email = build_email(summary)

    assert "<html>" in email.html_body
    assert "<h1>" in email.html_body
    assert "<p>" in email.html_body