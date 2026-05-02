"""
Full test suite for the ``summarizer`` module.

All tests are unit tests: external dependencies (Groq API, database) are
replaced with ``unittest.mock`` stubs so no real network calls are made.

Run with:
    pytest tests/llm/test_summarizer.py -v
"""

import sys
from unittest.mock import MagicMock, patch

import pytest


def _make_db(
    articles=None,
    subscriber_categories=None,
    latest_digest=None,
):
    """Create a mock database module with configurable return values."""
    db = MagicMock()
    db.get_articles_by_category.return_value = articles or []
    db.get_subscriber_categories.return_value = subscriber_categories or []
    db.get_latest_digest.return_value = latest_digest
    db.save_digest.return_value = None
    return db


def _make_completion_response(text):
    """Returns a minimal mock that mimics the Groq chat completion response."""
    response = MagicMock()
    response.choices[0].message.content = text
    return response


@pytest.fixture(autouse=True)
def _reset_summarizer_module():
    """Reload the module fresh for each test."""
    sys.modules.pop("src.llm.summarizer", None)


class TestGenerateCompletion:
    """Tests for the low-level completion helper."""

    def test_import_works_without_api_key(self, monkeypatch):
        """The module should remain importable when the key is missing."""
        monkeypatch.setenv("GROQ_API_KEY", "")
        sys.modules.pop("src.llm.summarizer", None)

        from src.llm import summarizer

        assert summarizer.summarize_chunk is not None

    def test_missing_api_key_raises_runtime_error(self, monkeypatch):
        """A missing key should fail when the API is actually needed."""
        monkeypatch.setenv("GROQ_API_KEY", "")
        sys.modules.pop("src.llm.summarizer", None)

        from src.llm.summarizer import _generate_completion

        with pytest.raises(RuntimeError, match="GROQ_API_KEY"):
            _generate_completion("system", "user", 10)

    def test_missing_chunk_prompt_raises_file_not_found_error(self):
        """A missing chunk prompt should fail with a clear FileNotFoundError."""
        from src.llm.summarizer import _get_chunk_prompt

        _get_chunk_prompt.cache_clear()
        with patch("src.llm.summarizer._load_prompt", side_effect=FileNotFoundError("missing")):
            with pytest.raises(FileNotFoundError, match="missing"):
                _get_chunk_prompt()

    def test_missing_digest_prompt_raises_file_not_found_error(self):
        """A missing digest prompt should fail with a clear FileNotFoundError."""
        from src.llm.summarizer import _get_digest_prompt

        _get_digest_prompt.cache_clear()
        with patch("src.llm.summarizer._load_prompt", side_effect=FileNotFoundError("missing")):
            with pytest.raises(FileNotFoundError, match="missing"):
                _get_digest_prompt()

    def test_invalid_response_structure_raises_runtime_error(self):
        """A response without choices should raise a clear RuntimeError."""
        response = MagicMock()
        response.choices = []

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = response

        with patch("src.llm.summarizer._get_client", return_value=mock_client):
            from src.llm.summarizer import _generate_completion

            with pytest.raises(RuntimeError, match="invalid response structure"):
                _generate_completion("system", "user", 10)

    def test_none_content_raises_runtime_error(self):
        """A response with ``None`` content should raise a clear RuntimeError."""
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = _make_completion_response(None)

        with patch("src.llm.summarizer._get_client", return_value=mock_client):
            from src.llm.summarizer import _generate_completion

            with pytest.raises(RuntimeError, match="empty response"):
                _generate_completion("system", "user", 10)


class TestSummarizeChunk:
    """Tests for the summarize_chunk function."""

    def test_returns_llm_response(self):
        """summarize_chunk should return the text provided by the helper call."""
        with patch(
            "src.llm.summarizer._generate_completion",
            return_value="Short summary.",
        ) as mock_generate:
            from src.llm.summarizer import summarize_chunk

            result = summarize_chunk(["Article 1", "Article 2"])

        assert result == "Short summary."
        mock_generate.assert_called_once()

    def test_uses_chunk_prompt_loader(self):
        """summarize_chunk should load the prompt lazily through the helper."""
        with (
            patch("src.llm.summarizer._get_chunk_prompt", return_value="chunk-prompt") as mock_prompt,
            patch("src.llm.summarizer._generate_completion", return_value="Short summary.") as mock_generate,
        ):
            from src.llm.summarizer import summarize_chunk

            summarize_chunk(["Article 1"])

        mock_prompt.assert_called_once()
        assert mock_generate.call_args.args[0] == "chunk-prompt"

    def test_articles_are_joined_with_separator(self):
        """Articles should be joined with '---' before being passed to the helper."""
        with patch("src.llm.summarizer._generate_completion", return_value="x") as mock_generate:
            from src.llm.summarizer import summarize_chunk

            summarize_chunk(["A", "B", "C"])

        user_content = mock_generate.call_args.args[1]
        assert "---" in user_content
        assert "A" in user_content
        assert "B" in user_content
        assert "C" in user_content

    def test_empty_list_returns_empty_string(self):
        """An empty input should produce no helper call and return an empty string."""
        with patch("src.llm.summarizer._generate_completion") as mock_generate:
            from src.llm.summarizer import summarize_chunk

            result = summarize_chunk([])

        mock_generate.assert_not_called()
        assert result == ""

    def test_single_article(self):
        """A single article should be processed correctly."""
        with patch(
            "src.llm.summarizer._generate_completion",
            return_value="Single article summary",
        ) as mock_generate:
            from src.llm.summarizer import summarize_chunk

            result = summarize_chunk(["Just one article"])

        assert result == "Single article summary"
        mock_generate.assert_called_once()


class TestSummarizeDigest:
    """Tests for the summarize_digest function."""

    def test_returns_llm_response(self):
        """summarize_digest should return the helper result."""
        with patch(
            "src.llm.summarizer._generate_completion",
            return_value="Overall digest",
        ) as mock_generate:
            from src.llm.summarizer import summarize_digest

            result = summarize_digest(["Summary 1", "Summary 2"])

        assert result == "Overall digest"
        mock_generate.assert_called_once()

    def test_uses_digest_prompt_loader(self):
        """summarize_digest should load the prompt lazily through the helper."""
        with (
            patch("src.llm.summarizer._get_digest_prompt", return_value="digest-prompt") as mock_prompt,
            patch("src.llm.summarizer._generate_completion", return_value="Overall digest") as mock_generate,
        ):
            from src.llm.summarizer import summarize_digest

            summarize_digest(["Summary 1"])

        mock_prompt.assert_called_once()
        assert mock_generate.call_args.args[0] == "digest-prompt"

    def test_summaries_are_joined(self):
        """Chunk summaries should be joined before being passed to the helper."""
        with patch("src.llm.summarizer._generate_completion", return_value="x") as mock_generate:
            from src.llm.summarizer import summarize_digest

            summarize_digest(["Part A", "Part B"])

        user_content = mock_generate.call_args.args[1]
        assert "Part A" in user_content
        assert "Part B" in user_content

    def test_empty_list_returns_empty_string(self):
        """Empty input should make no helper call and return an empty string."""
        with patch("src.llm.summarizer._generate_completion") as mock_generate:
            from src.llm.summarizer import summarize_digest

            result = summarize_digest([])

        mock_generate.assert_not_called()
        assert result == ""


class TestBuildCategoryDigest:
    """Tests for the build_category_digest function."""

    def test_invalid_category_raises_value_error(self):
        """Invalid categories should raise a ValueError."""
        from src.llm.summarizer import build_category_digest

        db = _make_db()
        with pytest.raises(ValueError, match="Invalid category"):
            build_category_digest(db, "INVALID")

    def test_zero_chunk_size_raises_value_error(self):
        """A chunk size of zero must be rejected."""
        from src.llm.summarizer import build_category_digest

        db = _make_db()
        with pytest.raises(ValueError, match="chunk_size"):
            build_category_digest(db, "SPORTS", chunk_size=0)

    def test_negative_chunk_size_raises_value_error(self):
        """A negative chunk size must be rejected."""
        from src.llm.summarizer import build_category_digest

        db = _make_db()
        with pytest.raises(ValueError, match="chunk_size"):
            build_category_digest(db, "SPORTS", chunk_size=-1)

    def test_no_articles_returns_info_message(self):
        """When no articles exist, an info message should be returned."""
        from src.llm.summarizer import build_category_digest

        db = _make_db(articles=[])
        result = build_category_digest(db, "SPORTS")
        assert "SPORTS" in result
        assert "available" in result.lower()

    def test_articles_with_empty_text_are_ignored(self):
        """Articles with no text should be filtered out."""
        from src.llm.summarizer import build_category_digest

        db = _make_db(articles=[{"text": ""}, {"text": None}])
        result = build_category_digest(db, "SPORTS")
        assert "available" in result.lower()

    def test_articles_without_text_key_are_ignored(self):
        """Articles missing the text key should also be ignored safely."""
        from src.llm.summarizer import build_category_digest

        db = _make_db(articles=[{}, {"text": ""}, {"text": None}])
        result = build_category_digest(db, "SPORTS")
        assert "available" in result.lower()

    def test_digest_is_saved_to_db(self):
        """The finished digest should be persisted to the database exactly once."""
        with (
            patch("src.llm.summarizer.summarize_chunk", return_value="chunk-summary"),
            patch("src.llm.summarizer.summarize_digest", return_value="final-digest"),
        ):
            from src.llm.summarizer import build_category_digest

            db = _make_db(articles=[{"text": "Article A"}])
            build_category_digest(db, "TECHNOLOGY")

        db.save_digest.assert_called_once_with("TECHNOLOGY", "final-digest")

    def test_lowercase_category_is_normalized(self):
        """Lowercase category names should be normalized to uppercase."""
        with (
            patch("src.llm.summarizer.summarize_chunk", return_value="chunk-summary"),
            patch("src.llm.summarizer.summarize_digest", return_value="final-digest"),
        ):
            from src.llm.summarizer import build_category_digest

            db = _make_db(articles=[{"text": "Article A"}])
            build_category_digest(db, "technology")

        db.get_articles_by_category.assert_called_once_with("TECHNOLOGY")
        db.save_digest.assert_called_once_with("TECHNOLOGY", "final-digest")

    def test_returns_digest_text(self):
        """build_category_digest should return the digest text."""
        with (
            patch("src.llm.summarizer.summarize_chunk", return_value="chunk-summary"),
            patch("src.llm.summarizer.summarize_digest", return_value="final-digest"),
        ):
            from src.llm.summarizer import build_category_digest

            db = _make_db(articles=[{"text": "Article A"}])
            result = build_category_digest(db, "TECHNOLOGY")

        assert result == "final-digest"

    def test_chunking_splits_articles_correctly(self):
        """Articles should be split into chunks of the correct size."""
        chunk_calls = []

        def fake_summarize_chunk(articles):
            chunk_calls.append(len(articles))
            return "summary"

        with (
            patch("src.llm.summarizer.summarize_chunk", side_effect=fake_summarize_chunk),
            patch("src.llm.summarizer.summarize_digest", return_value="digest"),
        ):
            from src.llm.summarizer import build_category_digest

            articles = [{"text": f"Article {i}"} for i in range(7)]
            db = _make_db(articles=articles)
            build_category_digest(db, "ECONOMY", chunk_size=3)

        assert chunk_calls == [3, 3, 1]

    def test_all_valid_categories_accepted(self):
        """All valid categories should be accepted without raising an error."""
        from src.llm.summarizer import VALID_CATEGORIES, build_category_digest

        for category in VALID_CATEGORIES:
            db = _make_db(articles=[])
            result = build_category_digest(db, category)
            assert isinstance(result, str)