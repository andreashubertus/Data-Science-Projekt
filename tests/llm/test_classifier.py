import pytest
from unittest.mock import MagicMock, patch
 
# Helpers:

def _make_groq_response(text: str) -> MagicMock:
    """Returns a minimal mock that mimics the Groq chat completion response."""
    response = MagicMock()
    response.choices[0].message.content = text
    return response
 
 
def _patch_client(return_text: str):
    """Context manager that patches ``src.llm.src.llm.src.llm.classifier.client`` and sets its return value."""
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = _make_groq_response(return_text)
    return patch("src.llm.src.llm.src.llm.classifier.client", mock_client)

# Tests: valid categories

class TestClassifyArticleValidCategories:
    """Tests that verify correct behaviour when the LLM returns a valid category."""
 
    @pytest.mark.parametrize("category", [
        "POLITICS", "ECONOMY", "TECHNOLOGY", "SPORTS", "CULTURE"
    ])
    def test_returns_valid_category(self, category: str):
        """
        For each of the five valid categories the function must return that
        exact string when the LLM responds with it.
        """
        with _patch_client(category):
            from src.llm.src.llm.src.llm.classifier import classify_article
            result = classify_article("Some article text.")
        assert result == category
 
    def test_strips_whitespace_from_response(self):
        """
        The function must strip leading/trailing whitespace from the LLM
        response before comparing it to the valid category set.
        For example '  SPORTS\\n' should resolve to 'SPORTS'.
        """
        with _patch_client("  SPORTS\n"):
            from src.llm.src.llm.src.llm.classifier import classify_article
            result = classify_article("Article about a football match.")
        assert result == "SPORTS"
 
    def test_lowercased_response_is_uppercased(self):
        """
        The function must upper-case the LLM response before matching, so
        'technology' and 'Technology' both resolve to 'TECHNOLOGY'.
        """
        with _patch_client("technology"):
            from src.llm.src.llm.src.llm.classifier import classify_article
            result = classify_article("Article about a new smartphone.")
        assert result == "TECHNOLOGY"
 
    def test_mixed_case_response_is_uppercased(self):
        """
        Mixed-case LLM responses such as 'eCONOMy' must be normalized to
        'ECONOMY' before validation.
        """
        with _patch_client("eCONOMy"):
            from src.llm.src.llm.src.llm.classifier import classify_article
            result = classify_article("Article about the stock market.")
        assert result == "ECONOMY"

# Tests: invalid / unexpected LLM responses

class TestClassifyArticleInvalidResponse:
    """Tests that verify the fallback behaviour for unrecognized LLM output."""
 
    def test_unknown_category_returns_fallback(self):
        """
        When the LLM returns a string that is not in VALID_CATEGORIES the
        function must return FALLBACK_CATEGORY instead of raising an error.
        """
        with _patch_client("UNKNOWN"):
            from src.llm.src.llm.src.llm.classifier import classify_article, FALLBACK_CATEGORY
            result = classify_article("Some article.")
        assert result == FALLBACK_CATEGORY
 
    def test_empty_llm_response_returns_fallback(self):
        """
        An empty string from the LLM is not a valid category and must trigger
        the fallback path.
        """
        with _patch_client(""):
            from src.llm.src.llm.src.llm.classifier import classify_article, FALLBACK_CATEGORY
            result = classify_article("Some article.")
        assert result == FALLBACK_CATEGORY
 
    def test_garbage_response_returns_fallback(self):
        """
        A completely nonsensical LLM response such as '!!!' must be treated
        as invalid and produce the fallback category.
        """
        with _patch_client("!!!"):
            from src.llm.src.llm.src.llm.classifier import classify_article, FALLBACK_CATEGORY
            result = classify_article("Some article.")
        assert result == FALLBACK_CATEGORY
 
    def test_multiword_response_returns_fallback(self):
        """
        If the LLM returns multiple words (e.g. 'I think SPORTS') the result
        won't match any single-word category and must fall back.
        """
        with _patch_client("I think SPORTS"):
            from src.llm.src.llm.src.llm.classifier import classify_article, FALLBACK_CATEGORY
            result = classify_article("Some article.")
        assert result == FALLBACK_CATEGORY
 
    def test_invalid_response_logs_warning(self, caplog):
        """
        When the fallback is triggered a warning must be written to the log so
        operators can detect systematic misclassification.
        """
        import logging
        with _patch_client("INVALID"), caplog.at_level(logging.WARNING, logger="src.llm.src.llm.src.llm.classifier"):
            from src.llm.src.llm.src.llm.classifier import classify_article
            classify_article("Some article.")
        assert any("unrecognized" in record.message.lower() for record in caplog.records)

# Tests: input validation

class TestClassifyArticleInputValidation:
    """Tests that verify early rejection of bad inputs."""
 
    def test_empty_string_raises_value_error(self):
        """
        An empty article string must raise a ValueError before any API call
        is made — sending blank text to the LLM would waste tokens and yield
        a meaningless result.
        """
        with patch("src.llm.src.llm.classifier.client") as mock_client:
            from src.llm.src.llm.classifier import classify_article
            with pytest.raises(ValueError, match="empty"):
                classify_article("")
            mock_client.chat.completions.create.assert_not_called()
 
    def test_whitespace_only_raises_value_error(self):
        """
        A string containing only whitespace (spaces, tabs, newlines) is
        semantically empty and must also raise a ValueError.
        """
        with patch("src.llm.src.llm.classifier.client") as mock_client:
            from src.llm.src.llm.classifier import classify_article
            with pytest.raises(ValueError):
                classify_article("   \n\t  ")
            mock_client.chat.completions.create.assert_not_called()

# Tests: API interaction

class TestClassifyArticleApiInteraction:
    """Tests that verify how the function interacts with the Groq API."""
 
    def test_article_text_is_sent_as_user_message(self):
        """
        The raw article text must appear in the 'user' role message that is
        sent to the API, so the LLM can read it.
        """
        with patch("src.llm.classifier.client") as mock_client:
            mock_client.chat.completions.create.return_value = _make_groq_response("SPORTS")
            from src.llm.classifier import classify_article
            classify_article("Breaking news about the Olympics.")
 
        messages = mock_client.chat.completions.create.call_args.kwargs["messages"]
        user_message = next(m for m in messages if m["role"] == "user")
        assert "Breaking news about the Olympics." in user_message["content"]
 
    def test_system_prompt_is_included(self):
        """
        A system-role message must be present in every API call so the LLM
        knows it should classify the article.
        """
        with patch("src.llm.classifier.client") as mock_client:
            mock_client.chat.completions.create.return_value = _make_groq_response("CULTURE")
            from src.llm.classifier import classify_article
            classify_article("Article about a new art exhibition.")
 
        messages = mock_client.chat.completions.create.call_args.kwargs["messages"]
        roles = [m["role"] for m in messages]
        assert "system" in roles
 
    def test_api_called_exactly_once(self):
        """
        Classifying a single article must result in exactly one API call —
        no retries or double-calls should occur under normal conditions.
        """
        with patch("src.llm.classifier.client") as mock_client:
            mock_client.chat.completions.create.return_value = _make_groq_response("POLITICS")
            from src.llm.classifier import classify_article
            classify_article("An article about the election.")
 
        mock_client.chat.completions.create.assert_called_once()