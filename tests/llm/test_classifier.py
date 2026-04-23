import pytest
from unittest.mock import MagicMock, patch
 
# Helpers:

def _make_groq_response(text: str) -> MagicMock:
    """Returns a minimal mock that mimics the Groq chat completion response."""
    response = MagicMock()
    response.choices[0].message.content = text
    return response
 
 
def _patch_client(return_text: str):
    """Context manager that patches ``classifier.client`` and sets its return value."""
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = _make_groq_response(return_text)
    return patch("classifier.client", mock_client)