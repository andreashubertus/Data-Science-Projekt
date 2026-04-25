"""
Unit tests for the ``classifier`` module.

The Groq API client is replaced with ``unittest.mock`` stubs, so no real
network calls are made.

Run with:
    pytest tests/llm/test_classifier.py -v
"""

import sys
from unittest.mock import MagicMock, patch

import pytest


def _make_groq_response(text) -> MagicMock:
    """Return a minimal mock that mimics a Groq chat completion response."""
    response = MagicMock()
    response.choices[0].message.content = text
    return response


def _make_client(return_text) -> MagicMock:
    """Return a mocked Groq client that yields ``return_text``."""
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = _make_groq_response(return_text)
    return mock_client


@pytest.fixture(autouse=True)
def _reset_classifier_module():
    """Reload the module fresh for each test."""
    sys.modules.pop("src.llm.classifier", None)


@pytest.mark.parametrize("category", ["POLITICS", "ECONOMY", "TECHNOLOGY", "SPORTS", "CULTURE"])
def test_returns_valid_category(category: str):
    """Each valid category should be returned unchanged."""
    with patch("src.llm.classifier._get_client", return_value=_make_client(category)):
        from src.llm.classifier import classify_article

        result = classify_article("Some article text.")

    assert result == category


def test_normalizes_llm_response():
    """Whitespace and casing from the model response should be normalized."""
    with patch("src.llm.classifier._get_client", return_value=_make_client("  technology\n")):
        from src.llm.classifier import classify_article

        result = classify_article("Article about a new smartphone.")

    assert result == "TECHNOLOGY"


@pytest.mark.parametrize("response_text", ["UNKNOWN", "", "!!!", "I think SPORTS"])
def test_invalid_category_returns_fallback(response_text: str):
    """Unrecognized model output should trigger the fallback value."""
    with patch("src.llm.classifier._get_client", return_value=_make_client(response_text)):
        from src.llm.classifier import FALLBACK_CATEGORY, classify_article

        result = classify_article("Some article.")

    assert result == FALLBACK_CATEGORY


def test_invalid_category_prints_warning(capsys):
    """Fallbacks should print a warning to support debugging."""
    with patch("src.llm.classifier._get_client", return_value=_make_client("INVALID")):
        from src.llm.classifier import classify_article

        classify_article("Some article.")

    assert "unrecognized" in capsys.readouterr().out.lower()


@pytest.mark.parametrize("article", ["", "   \n\t  "])
def test_blank_article_raises_value_error(article: str):
    """Blank article content should fail before any client lookup."""
    with patch("src.llm.classifier._get_client") as mock_get_client:
        from src.llm.classifier import classify_article

        with pytest.raises(ValueError, match="empty"):
            classify_article(article)

    mock_get_client.assert_not_called()


def test_missing_api_key_raises_runtime_error_on_call(monkeypatch):
    """A missing key should fail when the API is actually needed."""
    monkeypatch.setenv("GROQ_API_KEY", "")
    sys.modules.pop("src.llm.classifier", None)

    from src.llm.classifier import classify_article

    with pytest.raises(RuntimeError, match="GROQ_API_KEY"):
        classify_article("Some article.")


def test_get_client_creates_new_client_each_call(monkeypatch):
    """The Groq client should not be cached, matching the summarizer module."""
    monkeypatch.setenv("GROQ_API_KEY", "test-key")

    from src.llm.classifier import _get_client

    client_a = MagicMock()
    client_b = MagicMock()
    with patch("src.llm.classifier.Groq", side_effect=[client_a, client_b]) as mock_groq:
        assert _get_client() is client_a
        assert _get_client() is client_b

    assert mock_groq.call_count == 2


def test_invalid_response_structure_raises_runtime_error():
    """A response without choices should raise a clear RuntimeError."""
    response = MagicMock()
    response.choices = []

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = response

    with patch("src.llm.classifier._get_client", return_value=mock_client):
        from src.llm.classifier import classify_article

        with pytest.raises(RuntimeError, match="invalid response structure"):
            classify_article("Some article.")


def test_none_content_raises_runtime_error():
    """A response with ``None`` content should raise a clear RuntimeError."""
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = _make_groq_response(None)

    with patch("src.llm.classifier._get_client", return_value=mock_client):
        from src.llm.classifier import classify_article

        with pytest.raises(RuntimeError, match="empty response"):
            classify_article("Some article.")


def test_sends_prompt_and_article_to_api():
    """The API call should include both the system prompt and raw article text."""
    mock_client = _make_client("SPORTS")

    with patch("src.llm.classifier._get_client", return_value=mock_client):
        from src.llm.classifier import MODEL, MAX_TOKENS, classify_article

        classify_article("Breaking news about the Olympics.")

    mock_client.chat.completions.create.assert_called_once()
    call_kwargs = mock_client.chat.completions.create.call_args.kwargs

    assert call_kwargs["model"] == MODEL
    assert call_kwargs["max_tokens"] == MAX_TOKENS

    messages = call_kwargs["messages"]
    assert any(message["role"] == "system" and message["content"] for message in messages)
    assert any(
        message["role"] == "user" and "Breaking news about the Olympics." in message["content"]
        for message in messages
    )
