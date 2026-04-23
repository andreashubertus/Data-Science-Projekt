import pytest
from unittest.mock import MagigMock, patch, call

def _make_groq_response(text: str):
    """Creates a minimal mock object that mimics the Groq response structure."""
    response = MagicMock()
    response.choices[0].message.content = text
    return response

def _make_db(
    articles=None,
    subscriber_categories=None,
    latest_digest=None,
):
    """Creates a mock database module with configurable return values."""
    db = MagicMock()
    db.get_articles_by_category.return_value = articles or []
    db.get_subscriber_categories.return_value = subscriber_categories or []
    db.get_latest_digest.return_value = latest_digest
    db.save_digest.return_value = None
    return db