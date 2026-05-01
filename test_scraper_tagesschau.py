import pytest
from unittest.mock import MagicMock, patch
from scraper_tagesschau import *
import requests
from bs4 import BeautifulSoup

def make_mock_request(html: str, status_code: int = 200) -> MagicMock:
    mock = MagicMock()
    mock.status_code = status_code
    mock.text = html
    return mock

