"""
Full test suite for the ``summarizer`` module.
 
All tests are unit tests: external dependencies (Groq API, database) are
replaced with ``unittest.mock`` stubs so no real network calls are made.
 
Run with:
    pytest tests/test_summarizer.py -v
"""
 
import pytest
from unittest.mock import MagicMock, patch, call

# Helpers / Fixtures:

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


# Tests: summarize_chunk

class TestSummarizeChunk:
    """Tests for the summarize_chunk function."""

    def test_returns_llm_response(self):
        """summarize_chunk should return the text provided by the LLM."""
        with patch("src.llm.summarizer.client") as mock_client:
            mock_client.chat.completions.create.return_value = _make_groq_response(
                "Short summary."
            )
            from src.llm.summarizer import summarize_chunk
            result = summarize_chunk(["Article 1", "Article 2"])
        assert result == "Short summary."
 
    def test_articles_are_joined_with_separator(self):
        """Articles should be joined with '---' before being sent to the API."""
        with patch("src.llm.summarizer.client") as mock_client:
            mock_client.chat.completions.create.return_value = _make_groq_response("x")
            from src.llm.summarizer import summarize_chunk
            summarize_chunk(["A", "B", "C"])
 
        call_kwargs = mock_client.chat.completions.create.call_args
        user_content = call_kwargs.kwargs["messages"][1]["content"]
        assert "---" in user_content
        assert "A" in user_content
        assert "B" in user_content
        assert "C" in user_content
 
    def test_empty_list_returns_empty_string(self):
        """An empty input should produce no API call and return an empty string."""
        with patch("src.llm.summarizer.client") as mock_client:
            from src.llm.summarizer import summarize_chunk
            result = summarize_chunk([])
        mock_client.chat.completions.create.assert_not_called()
        assert result == ""
 
    def test_single_article(self):
        """A single article should be processed correctly."""
        with patch("src.llm.summarizer.client") as mock_client:
            mock_client.chat.completions.create.return_value = _make_groq_response(
                "Single article summary"
            )
            from src.llm.summarizer import summarize_chunk
            result = summarize_chunk(["Just one article"])
        assert result == "Single article summary"


# Tests: summarize_digest

class TestSummarizeDigest:
    """Tests for the summarize_digest function."""
 
    def test_returns_llm_response(self):
        """summarize_digest should return the LLM text."""
        with patch("src.llm.summarizer.client") as mock_client:
            mock_client.chat.completions.create.return_value = _make_groq_response(
                "Overall digest"
            )
            from src.llm.summarizer import summarize_digest
            result = summarize_digest(["Summary 1", "Summary 2"])
        assert result == "Overall digest"
 
    def test_summaries_are_joined(self):
        """Chunk summaries should be joined before being sent to the API."""
        with patch("src.llm.summarizer.client") as mock_client:
            mock_client.chat.completions.create.return_value = _make_groq_response("x")
            from src.llm.summarizer import summarize_digest
            summarize_digest(["Part A", "Part B"])
 
        user_content = (
            mock_client.chat.completions.create.call_args.kwargs["messages"][1]["content"]
        )
        assert "Part A" in user_content
        assert "Part B" in user_content
 
    def test_empty_list_returns_empty_string(self):
        """Empty input → no API call, empty string returned."""
        with patch("src.llm.summarizer.client") as mock_client:
            from src.llm.summarizer import summarize_digest
            result = summarize_digest([])
        mock_client.chat.completions.create.assert_not_called()
        assert result == ""


# Tests: build_category_digest

class TestBuildCategoryDigest:
    """Tests for the build_category_digest function."""
 
    def test_invalid_category_raises_value_error(self):
        """Invalid categories should raise a ValueError."""
        from src.llm.summarizer import build_category_digest
        db = _make_db()
        with pytest.raises(ValueError, match="Invalid category"):
            build_category_digest(db, "INVALID")
 
    def test_no_articles_returns_info_message(self):
        """When no articles exist, an info message should be returned."""
        from src.llm.summarizer import build_category_digest
        db = _make_db(articles=[])
        result = build_category_digest(db, "SPORTS")
        assert "SPORTS" in result
        assert "available" in result.lower()
 
    def test_articles_with_empty_text_are_ignored(self):
        """Articles with no text (None or empty string) should be filtered out."""
        from src.llm.summarizer import build_category_digest
        db = _make_db(articles=[{"text": ""}, {"text": None}])
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
 
        # 7 articles with chunk_size=3 → chunks of size 3, 3, 1
        assert chunk_calls == [3, 3, 1]
 
    def test_all_valid_categories_accepted(self):
        """All valid categories should be accepted without raising an error."""
        from src.llm.summarizer import build_category_digest, VALID_CATEGORIES
        for category in VALID_CATEGORIES:
            db = _make_db(articles=[])
            result = build_category_digest(db, category)
            assert isinstance(result, str)


# Tests: build_all_digests

class TestBuildAllDigests:
    """Tests for the build_all_digests function."""
 
    def test_returns_digest_for_every_category(self):
        """There should be one entry in the result dict for every valid category."""
        from src.llm.summarizer import build_all_digests, VALID_CATEGORIES
        with patch("src.llm.summarizer.build_category_digest", return_value="digest") as mock_bcd:
            db = _make_db()
            result = build_all_digests(db)
 
        assert set(result.keys()) == VALID_CATEGORIES
        assert mock_bcd.call_count == len(VALID_CATEGORIES)
 
    def test_chunk_size_is_passed_through(self):
        """The chunk_size parameter should be forwarded to build_category_digest."""
        from src.llm.summarizer import build_all_digests
        with patch("src.llm.summarizer.build_category_digest", return_value="d") as mock_bcd:
            db = _make_db()
            build_all_digests(db, chunk_size=10)
 
        for c in mock_bcd.call_args_list:
            assert c.args[2] == 10 or c.kwargs.get("chunk_size") == 10


# Tests: build_newsletter_for_subscriber

class TestBuildNewsletterForSubscriber:
    """Tests for the build_newsletter_for_subscriber function."""
 
    def test_no_subscriptions_returns_info_message(self):
        """Without any subscriptions an appropriate message should be returned."""
        from src.llm.summarizer import build_newsletter_for_subscriber
        db = _make_db(subscriber_categories=[])
        result = build_newsletter_for_subscriber(db, "user@example.com")
        assert "no" in result.lower() or "none" in result.lower() or "subscription" in result.lower()
 
    def test_no_digests_available_returns_info_message(self):
        """When no digests exist in the database an info message should follow."""
        from src.llm.summarizer import build_newsletter_for_subscriber
        db = _make_db(
            subscriber_categories=["SPORTS", "CULTURE"],
            latest_digest=None,
        )
        result = build_newsletter_for_subscriber(db, "user@example.com")
        assert "digest" in result.lower() or "available" in result.lower()
 
    def test_newsletter_contains_category_headings(self):
        """The newsletter should contain a Markdown heading for each category."""
        from src.llm.summarizer import build_newsletter_for_subscriber
        db = _make_db(
            subscriber_categories=["SPORTS"],
            latest_digest="Latest sports news.",
        )
        result = build_newsletter_for_subscriber(db, "user@example.com")
        assert "## Sports" in result
        assert "Latest sports news." in result
 
    def test_multiple_categories_are_separated(self):
        """Multiple categories should be separated by '---'."""
        from src.llm.summarizer import build_newsletter_for_subscriber
 
        db = MagicMock()
        db.get_subscriber_categories.return_value = ["SPORTS", "CULTURE"]
        db.get_latest_digest.side_effect = lambda cat: f"Digest for {cat}"
 
        result = build_newsletter_for_subscriber(db, "user@example.com")
        assert "---" in result
        assert "## Sports" in result
        assert "## Culture" in result
 
    def test_categories_without_digest_are_skipped(self):
        """Categories without an existing digest should be absent from the newsletter."""
        from src.llm.summarizer import build_newsletter_for_subscriber
 
        db = MagicMock()
        db.get_subscriber_categories.return_value = ["SPORTS", "CULTURE"]
        # Only SPORTS has a digest
        db.get_latest_digest.side_effect = lambda cat: (
            "Sports digest" if cat == "SPORTS" else None
        )
 
        result = build_newsletter_for_subscriber(db, "user@example.com")
        assert "## Sports" in result
        assert "## Culture" not in result
 
    def test_correct_email_is_queried(self):
        """The correct email address should be passed to the database."""
        from src.llm.summarizer import build_newsletter_for_subscriber
        db = _make_db(subscriber_categories=[])
        build_newsletter_for_subscriber(db, "test@domain.com")
        db.get_subscriber_categories.assert_called_once_with("test@domain.com")
