import pytest
from unittest.mock import MagicMock, patch
 
# Helpers:

def _make_groq_response(text: str) -> MagicMock:
    """Returns a minimal mock that mimics the Groq chat completion response."""
    response = MagicMock()
    response.choices[0].message.content = text
    return response
 
 
def _patch_client(return_text: str):
    """Context manager that patches ``src.llm.classifier.client`` and sets its return value."""
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = _make_groq_response(return_text)
    return patch("src.llm.classifier.client", mock_client)

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
            from src.llm.classifier import classify_article
            result = classify_article("Some article text.")
        assert result == category
 
    def test_strips_whitespace_from_response(self):
        """
        The function must strip leading/trailing whitespace from the LLM
        response before comparing it to the valid category set.
        For example '  SPORTS\\n' should resolve to 'SPORTS'.
        """
        with _patch_client("  SPORTS\n"):
            from src.llm.classifier import classify_article
            result = classify_article("Article about a football match.")
        assert result == "SPORTS"
 
    def test_lowercased_response_is_uppercased(self):
        """
        The function must upper-case the LLM response before matching, so
        'technology' and 'Technology' both resolve to 'TECHNOLOGY'.
        """
        with _patch_client("technology"):
            from src.llm.classifier import classify_article
            result = classify_article("Article about a new smartphone.")
        assert result == "TECHNOLOGY"
 
    def test_mixed_case_response_is_uppercased(self):
        """
        Mixed-case LLM responses such as 'eCONOMy' must be normalized to
        'ECONOMY' before validation.
        """
        with _patch_client("eCONOMy"):
            from src.llm.classifier import classify_article
            result = classify_article("Article about the stock market.")
        assert result == "ECONOMY"