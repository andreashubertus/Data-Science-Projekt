"""
Full test suite for the ``classifier`` module.

All tests are unit tests: the Groq API client is replaced with
``unittest.mock`` stubs so no real network calls are made.

Run with:
    pytest tests/test_classifier.py -v
"""

import sys
from unittest.mock import MagicMock, patch

import pytest


def _make_groq_response(text) -> MagicMock:
    """Returns a minimal mock that mimics the Groq chat completion response."""
    response = MagicMock()
    response.choices[0].message.content = text
    return response


def _patch_client(return_text):
    """Patch ``src.llm.classifier._get_client`` and set its return value."""
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = _make_groq_response(return_text)
    return patch("src.llm.classifier._get_client", return_value=mock_client)


@pytest.fixture(autouse=True)
def _reset_classifier_module():
    """Reload the module fresh for each test."""
    sys.modules.pop("src.llm.classifier", None)


class TestClassifyArticleValidCategories:
    """Tests that verify correct behaviour when the LLM returns a valid category."""

    @pytest.mark.parametrize("category", ["POLITICS", "ECONOMY", "TECHNOLOGY", "SPORTS", "CULTURE"])
    def test_returns_valid_category(self, category: str):
        """Each valid category should be returned unchanged."""
        with _patch_client(category):
            from src.llm.classifier import classify_article

            result = classify_article("Some article text.")

        assert result == category

    def test_strips_whitespace_from_response(self):
        """Leading and trailing whitespace should be ignored."""
        with _patch_client("  SPORTS\n"):
            from src.llm.classifier import classify_article

            result = classify_article("Article about a football match.")

        assert result == "SPORTS"

    def test_lowercased_response_is_uppercased(self):
        """Lowercase model output should be normalized."""
        with _patch_client("technology"):
            from src.llm.classifier import classify_article

            result = classify_article("Article about a new smartphone.")

        assert result == "TECHNOLOGY"

    def test_mixed_case_response_is_uppercased(self):
        """Mixed-case model output should be normalized."""
        with _patch_client("eCONOMy"):
            from src.llm.classifier import classify_article

            result = classify_article("Article about the stock market.")

        assert result == "ECONOMY"


class TestClassifyArticleInvalidResponse:
    """Tests that verify the fallback behaviour for unrecognized LLM output."""

    def test_unknown_category_returns_fallback(self):
        """An unknown category should trigger the fallback value."""
        with _patch_client("UNKNOWN"):
            from src.llm.classifier import FALLBACK_CATEGORY, classify_article

            result = classify_article("Some article.")

        assert result == FALLBACK_CATEGORY

    def test_empty_llm_response_returns_fallback(self):
        """An empty string is still a handled invalid category."""
        with _patch_client(""):
            from src.llm.classifier import FALLBACK_CATEGORY, classify_article

            result = classify_article("Some article.")

        assert result == FALLBACK_CATEGORY

    def test_garbage_response_returns_fallback(self):
        """Garbage text should trigger the fallback value."""
        with _patch_client("!!!"):
            from src.llm.classifier import FALLBACK_CATEGORY, classify_article

            result = classify_article("Some article.")

        assert result == FALLBACK_CATEGORY

    def test_multiword_response_returns_fallback(self):
        """Multi-word output should trigger the fallback value."""
        with _patch_client("I think SPORTS"):
            from src.llm.classifier import FALLBACK_CATEGORY, classify_article

            result = classify_article("Some article.")

        assert result == FALLBACK_CATEGORY

    def test_invalid_response_prints_warning(self, capsys):
        """Fallbacks should print a warning to support debugging."""
        with _patch_client("INVALID"):
            from src.llm.classifier import classify_article

            classify_article("Some article.")

        assert "unrecognized" in capsys.readouterr().out.lower()


class TestClassifyArticleInputValidation:
    """Tests that verify early rejection of bad inputs."""

    def test_empty_string_raises_value_error(self):
        """An empty article should fail before any client lookup."""
        with patch("src.llm.classifier._get_client") as mock_get_client:
            from src.llm.classifier import classify_article

            with pytest.raises(ValueError, match="empty"):
                classify_article("")

        mock_get_client.assert_not_called()

    def test_whitespace_only_raises_value_error(self):
        """Blank article content should fail before any client lookup."""
        with patch("src.llm.classifier._get_client") as mock_get_client:
            from src.llm.classifier import classify_article

            with pytest.raises(ValueError):
                classify_article("   \n\t  ")

        mock_get_client.assert_not_called()

    def test_import_works_without_api_key(self, monkeypatch):
        """The module should remain importable when the key is missing."""
        monkeypatch.setenv("GROQ_API_KEY", "")
        sys.modules.pop("src.llm.classifier", None)

        from src.llm import classifier

        assert classifier.classify_article is not None

    def test_missing_api_key_raises_runtime_error_on_call(self, monkeypatch):
        """A missing key should fail when the API is actually needed."""
        monkeypatch.setenv("GROQ_API_KEY", "")
        sys.modules.pop("src.llm.classifier", None)

        from src.llm.classifier import classify_article

        with pytest.raises(RuntimeError, match="GROQ_API_KEY"):
            classify_article("Some article.")


class TestClassifyArticleApiErrors:
    """Tests that verify behaviour for malformed API responses."""

    def test_missing_choices_raises_runtime_error(self):
        """A response without choices should raise a clear RuntimeError."""
        response = MagicMock()
        response.choices = []

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = response

        with patch("src.llm.classifier._get_client", return_value=mock_client):
            from src.llm.classifier import classify_article

            with pytest.raises(RuntimeError, match="invalid response structure"):
                classify_article("Some article.")

    def test_none_content_raises_runtime_error(self):
        """A response with ``None`` content should raise a clear RuntimeError."""
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = _make_groq_response(None)

        with patch("src.llm.classifier._get_client", return_value=mock_client):
            from src.llm.classifier import classify_article

            with pytest.raises(RuntimeError, match="empty response"):
                classify_article("Some article.")


class TestClassifyArticleApiInteraction:
    """Tests that verify how the function interacts with the Groq API."""

    def test_article_text_is_sent_as_user_message(self):
        """The raw article text must be sent as the user message."""
        with patch("src.llm.classifier._get_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = _make_groq_response("SPORTS")
            mock_get_client.return_value = mock_client

            from src.llm.classifier import classify_article

            classify_article("Breaking news about the Olympics.")

        messages = mock_client.chat.completions.create.call_args.kwargs["messages"]
        user_message = next(m for m in messages if m["role"] == "user")
        assert "Breaking news about the Olympics." in user_message["content"]

    def test_system_prompt_is_included(self):
        """A system-role message must be present in every API call."""
        with patch("src.llm.classifier._get_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = _make_groq_response("CULTURE")
            mock_get_client.return_value = mock_client

            from src.llm.classifier import classify_article

            classify_article("Article about a new art exhibition.")

        messages = mock_client.chat.completions.create.call_args.kwargs["messages"]
        roles = [m["role"] for m in messages]
        assert "system" in roles

    def test_api_called_exactly_once(self):
        """Classifying a single article should perform exactly one API call."""
        with patch("src.llm.classifier._get_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = _make_groq_response("POLITICS")
            mock_get_client.return_value = mock_client

            from src.llm.classifier import classify_article

            classify_article("An article about the election.")

        mock_client.chat.completions.create.assert_called_once()
