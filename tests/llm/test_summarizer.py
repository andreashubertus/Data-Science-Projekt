import pytest
from unittest.mock import MagigMock, patch, call

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
        with patch("summarizer.client") as mock_client:
            mock_client.chat.completions.create.return_value = _make_groq_response(
                "Short summary."
            )
            from summarizer import summarize_chunk
            result = summarize_chunk(["Article 1", "Article 2"])
        assert result == "Short summary."
 
    def test_articles_are_joined_with_separator(self):
        """Articles should be joined with '---' before being sent to the API."""
        with patch("summarizer.client") as mock_client:
            mock_client.chat.completions.create.return_value = _make_groq_response("x")
            from summarizer import summarize_chunk
            summarize_chunk(["A", "B", "C"])
 
        call_kwargs = mock_client.chat.completions.create.call_args
        user_content = call_kwargs.kwargs["messages"][1]["content"]
        assert "---" in user_content
        assert "A" in user_content
        assert "B" in user_content
        assert "C" in user_content
 
    def test_empty_list_returns_empty_string(self):
        """An empty input should produce no API call and return an empty string."""
        with patch("summarizer.client") as mock_client:
            from summarizer import summarize_chunk
            result = summarize_chunk([])
        mock_client.chat.completions.create.assert_not_called()
        assert result == ""
 
    def test_single_article(self):
        """A single article should be processed correctly."""
        with patch("summarizer.client") as mock_client:
            mock_client.chat.completions.create.return_value = _make_groq_response(
                "Single article summary"
            )
            from summarizer import summarize_chunk
            result = summarize_chunk(["Just one article"])
        assert result == "Single article summary"

# Tests: summarize_digest

class TestSummarizeDigest:
    """Tests for the summarize_digest function."""
 
    def test_returns_llm_response(self):
        """summarize_digest should return the LLM text."""
        with patch("summarizer.client") as mock_client:
            mock_client.chat.completions.create.return_value = _make_groq_response(
                "Overall digest"
            )
            from summarizer import summarize_digest
            result = summarize_digest(["Summary 1", "Summary 2"])
        assert result == "Overall digest"
 
    def test_summaries_are_joined(self):
        """Chunk summaries should be joined before being sent to the API."""
        with patch("summarizer.client") as mock_client:
            mock_client.chat.completions.create.return_value = _make_groq_response("x")
            from summarizer import summarize_digest
            summarize_digest(["Part A", "Part B"])
 
        user_content = (
            mock_client.chat.completions.create.call_args.kwargs["messages"][1]["content"]
        )
        assert "Part A" in user_content
        assert "Part B" in user_content
 
    def test_empty_list_returns_empty_string(self):
        """Empty input → no API call, empty string returned."""
        with patch("summarizer.client") as mock_client:
            from summarizer import summarize_digest
            result = summarize_digest([])
        mock_client.chat.completions.create.assert_not_called()
        assert result == ""

