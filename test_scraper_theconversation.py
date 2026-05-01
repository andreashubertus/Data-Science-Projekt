import pytest
from unittest.mock import MagicMock, patch
from scraper_theconversation import *
import requests
from bs4 import BeautifulSoup

def make_mock_request(content, status_code = 200, is_bytes = False) -> MagicMock:
    mock = MagicMock()
    mock.status_code = status_code
    if is_bytes:
        mock.content = content
    else:
        mock.text = content
        mock.content = content.encode("utf-8") if isinstance(content, str) else content
    return mock
