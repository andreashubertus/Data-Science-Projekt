"""Integration tests for the LLM components using the real Groq API.

These tests complement the mock-based unit tests by checking that the
classifier and summarizer work end-to-end with actual API calls. They only
assert stable properties of the responses, because exact LLM output can vary.
"""

import os

import pytest
from dotenv import load_dotenv


pytestmark = pytest.mark.integration

load_dotenv()


def _require_groq_api_key() -> None:
    """Skip the test when no Groq API key is available in the environment."""
    if not os.environ.get("GROQ_API_KEY"):
        pytest.skip("GROQ_API_KEY not set; skipping Groq integration test.")


def test_classifier_returns_category() -> None:
    """Classifier should return a valid category or the defined fallback value."""
    _require_groq_api_key()

    from src.llm.classifier import (
        FALLBACK_CATEGORY,
        VALID_CATEGORIES,
        classify_article,
    )

    article = (
        "The government presented a new budget package with tax reforms, "
        "infrastructure spending, and economic relief for small businesses."
    )

    result = classify_article(article)

    assert result in VALID_CATEGORIES | {FALLBACK_CATEGORY}

def test_summarize_chunk_returns_non_empty_text() -> None:
    """Chunk summarization should produce a non-empty string for normal input."""
    _require_groq_api_key()

    from src.llm.summarizer import summarize_chunk

    articles = [
        "Team A defeated Team B 2 to 1 after a late goal in the final minutes.",
        "The coach praised the disciplined defense and strong second-half performance.",
    ]

    result = summarize_chunk(articles)

    assert isinstance(result, str)
    assert result.strip() != ""


def test_summarize_digest_returns_non_empty_text() -> None:
    """Digest summarization should combine partial summaries into readable output."""
    _require_groq_api_key()

    from src.llm.summarizer import summarize_digest

    chunk_summaries = [
        "Sports: Team A won an important match and improved its league position.",
        "Sports: The coach highlighted defensive stability and team spirit.",
    ]

    result = summarize_digest(chunk_summaries)

    assert isinstance(result, str)
    assert result.strip() != ""
