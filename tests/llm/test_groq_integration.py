import os

import pytest
from dotenv import load_dotenv


pytestmark = pytest.mark.integration

load_dotenv()


def _require_groq_api_key() -> None:
    """Skip the test when no Groq API key is available in the environment."""
    if not os.environ.get("GROQ_API_KEY"):
        pytest.skip("GROQ_API_KEY not set; skipping Groq integration test.")


def test_classifier_with_real_groq_returns_known_category() -> None:
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