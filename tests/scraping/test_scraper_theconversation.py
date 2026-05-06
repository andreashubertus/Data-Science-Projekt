import pytest
from unittest.mock import MagicMock, patch
from src.scraper.scraper_theconversation import *
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


class TestGetLinksFromTheConversationRss:

    RSS_OK = """<?xml version="1.0" encoding="UTF-8"?>
    <feed xmlns="http://www.w3.org/2005/Atom">
        <link rel="alternate" href="https://theconversation.com"/>
        <link rel="alternate" href="https://theconversation.com/article-one-123"/>
        <link rel="alternate" href="https://theconversation.com/article-two-456"/>
    </feed>"""

    def test_returns_filtered_links(self):
        mock = make_mock_request(self.RSS_OK, is_bytes=True)
        links, error = get_links_from_theconversation_rss(request=mock)
        assert error == ""
        assert len(links) == 2
        assert "https://theconversation.com" not in links
        assert "https://theconversation.com/article-one-123" in links
        assert "https://theconversation.com/article-two-456" in links

    def test_returns_links_from_nested_atom_entries(self):
        rss_nested = """<?xml version="1.0" encoding="UTF-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
            <link rel="alternate" href="https://theconversation.com"/>
            <entry>
                <title>Article One</title>
                <link rel="alternate" href="https://theconversation.com/article-one-123"/>
            </entry>
            <entry>
                <title>Article Two</title>
                <link rel="alternate" href="https://theconversation.com/article-two-456"/>
            </entry>
        </feed>"""
        mock = make_mock_request(rss_nested, is_bytes=True)
        links, error = get_links_from_theconversation_rss(request=mock)
        assert error == ""
        assert links == [
            "https://theconversation.com/article-one-123",
            "https://theconversation.com/article-two-456",
        ]

    def test_returns_error_on_bad_status_code(self):
        mock = make_mock_request(self.RSS_OK, status_code=503, is_bytes=True)
        links, error = get_links_from_theconversation_rss(request=mock)
        assert links is None
        assert "Keine Antwort vom TheConversation RSS-Feed. Status Code: 503" in error

    def test_returns_error_on_request_exception(self):
        with patch("src.scraper.scraper_theconversation.requests.get", side_effect=requests.RequestException("network down")):
            links, error = get_links_from_theconversation_rss()
        assert links is None
        assert "Fehler beim Abrufen des TheConversation RSS-Feeds" in error

    def test_returns_error_on_empty_feed(self):
        empty_rss = """<?xml version="1.0" encoding="UTF-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
            <link rel="alternate" href="https://theconversation.com"/>
        </feed>"""
        mock = make_mock_request(empty_rss, is_bytes=True)
        links, error = get_links_from_theconversation_rss(request=mock)
        assert links is None
        assert "Keine Artikel im TheConversation RSS-Feed gefunden" in error
    
    def test_returns_error_when_only_base_url_in_feed(self):
        rss_only_base = """<?xml version="1.0" encoding="UTF-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
            <link rel="alternate" href="https://theconversation.com"/>
            <link rel="alternate" href="https://theconversation.com"/>
        </feed>"""
        mock = make_mock_request(rss_only_base, is_bytes=True)
        links, error = get_links_from_theconversation_rss(request=mock)
        assert links is None
        assert "Keine Artikel im TheConversation RSS-Feed gefunden" in error


class TestGetArticleHeadline:
    def test_returns_headline_on_success(self):
        html = '<h1 class="entry-title">Test Artikel Überschrift</h1>'
        soup = BeautifulSoup(html, "html.parser")
        headline, error, issues = get_article_headline(soup, "test-link", "", 0)
        assert headline == "Test Artikel Überschrift"
        assert error == ""
        assert issues == 0

    def test_returns_error_when_not_found(self):
        html = '<div class="wrong-class">Keine Überschrift hier</div>'
        soup = BeautifulSoup(html, "html.parser")
        headline, error, issues = get_article_headline(soup, "test-link", "Vorheriger Fehler. ", 0)
        assert headline is None
        assert "Keine Überschrift gefunden" in error
        assert "test-link" in error
        assert issues == 1
    

class TestGetArticleText:
    def test_returns_text_on_success(self):
        html = '''
        <div itemprop="articleBody">
            <p>Hier geht es um einen Testartikel. Dieser ist sehr interessant.</p>
            <p>Zweiter Absatz.</p>
        </div>
        '''
        soup = BeautifulSoup(html, "html.parser")
        text, error, issues = get_article_text(soup, "test-link", "", 0)
        assert text == "\nHier geht es um einen Testartikel. Dieser ist sehr interessant.\nZweiter Absatz."
        assert error == ""
        assert issues == 0

    def test_returns_error_when_no_article_body(self):
        html = '<div class="wrong-class">Kein Artikeltext hier</div>'
        soup = BeautifulSoup(html, "html.parser")
        text, error, issues = get_article_text(soup, "test-link", "Vorheriger Fehler. ", 0)
        assert text == ""
        assert "Keine Artikeltext gefunden" in error
        assert "test-link" in error
        assert issues == 1
    
    def test_returns_error_when_no_paragraphs(self):
        html = '<div itemprop="articleBody">Kein Absatz hier</div>'
        soup = BeautifulSoup(html, "html.parser")
        text, error, issues = get_article_text(soup, "test-link", "Vorheriger Fehler. ", 0)
        assert text == ""
        assert "Keine Absätze gefunden" in error
        assert "test-link" in error
        assert issues == 1
    
    def test_returns_error_when_text_too_short(self):
        html = '''
        <div itemprop="articleBody">
            <p>Kurz</p>
        </div>
        '''
        soup = BeautifulSoup(html, "html.parser")
        text, error, issues = get_article_text(soup, "test-link", "Vorheriger Fehler. ", 0)
        assert text == "\nKurz"
        assert "Artikeltext zu kurz" in error
        assert "test-link" in error
        assert issues == 1

    def test_returns_text_strips_whitespace(self):
        html = '''
        <div itemprop="articleBody">
            <p>   Hier ist ein Absatz mit führenden und folgenden Leerzeichen.   </p>
            <p>   Zweiter Absatz mit Leerzeichen.   </p>
        </div>
        '''
        soup = BeautifulSoup(html, "html.parser")
        text, error, issues = get_article_text(soup, "test-link", "", 0)
        assert text == "\nHier ist ein Absatz mit führenden und folgenden Leerzeichen.\nZweiter Absatz mit Leerzeichen."
        assert error == ""
        assert issues == 0

    def test_returns_error_when_text_only_whitespace(self):
        html = '''
        <div itemprop="articleBody"><p>       </p><p>   </p></div>
        '''
        soup = BeautifulSoup(html, "html.parser")
        text, error, issues = get_article_text(soup, "test-link", "Vorheriger Fehler. ", 0)
        assert text == ""
        assert "Artikeltext zu kurz" in error
        assert "test-link" in error
        assert issues == 1


    def test_strips_whitespace_from_paragraphs(self):
        html = '''
        <div itemprop="articleBody">
            <p>   Erster Absatz mit Leerzeichen.   </p>
            <p>   Zweiter Absatz mit Leerzeichen.   </p>
        </div>
        '''
        soup = BeautifulSoup(html, "html.parser")
        text, error, issues = get_article_text(soup, "test-link", "", 0)
        assert text == "\nErster Absatz mit Leerzeichen.\nZweiter Absatz mit Leerzeichen."
        assert error == ""
        assert issues == 0

    def test_skips_empty_paragraphs(self):
        html = """
        <div itemprop="articleBody">
            <p>    </p>
            <p>Dies ist ein ausreichend langer Absatz mit echtem Inhalt fuer den Test.</p>
        </div>
        """
        soup = BeautifulSoup(html, "html.parser")
        text, error, issues = get_article_text(soup, "link", "", 0)
        assert text.strip().startswith("Dies ist")
        assert issues == 0


class TestGetArticleDate:
    def test_returns_date_on_success(self):
        html = """
        <time datetime="2024-06-01T12:00:00Z">1. Juni 2024</time>
        """
        soup = BeautifulSoup(html, "html.parser")
        date, error, issues = get_article_date(soup, "test-link", "", 0)
        assert date == "1. Juni 2024"
        assert error == ""
        assert issues == 0

    def test_returns_error_when_no_time_tag(self):
        html = """
        <div>Kein time-Tag hier</div>
        """
        soup = BeautifulSoup(html, "html.parser")
        date, error, issues = get_article_date(soup, "test-link", "", 0)
        assert "Kein Datum gefunden" in date
        assert f"Kein Datum gefunden, überspringe Artikel: test-link.\n" in error
        assert "test-link" in error
        assert issues == 1

    def test_returns_error_when_time_tag_has_no_datetime_attr(self):
        html = """"
        <time>Am 8. Mai 2024 ist Portfoliopräsentation</time>
        """
        soup = BeautifulSoup(html, "html.parser")
        date, error, issues = get_article_date(soup, "test-link", "", 0)
        assert "Kein Datum gefunden" in date
        assert f"Kein Datum gefunden, überspringe Artikel: test-link.\n" in error
        assert "test-link" in error
        assert issues == 1


class TestScrapeArticle:
    article_html_ok = """
    <html><body>
        <h1 class="entry-title">Ein vollständiger Artikel</h1>
        <time datetime="2024-06-01">June 1, 2024</time>
        <div itemprop="articleBody">
            <p>Dies ist der erste Absatz mit ausreichend Text für einen erfolgreichen Scrape-Test.</p>
            <p>Und hier ist noch ein zweiter Absatz damit der Text wirklich lang genug ist.</p>
        </div>
    </body></html>"""

    def test_returns_article_data_on_success(self):
        mock_request = make_mock_request(self.article_html_ok)
        article_data, error_message = scrape_article("https://theconversation.com/test-article", article_request=mock_request)
        assert error_message == ""
        assert article_data[0] == "Ein vollständiger Artikel"
        assert article_data[3] == "Dies ist der erste Absatz mit ausreichend Text für einen erfolgreichen Scrape-Test.\nUnd hier ist noch ein zweiter Absatz damit der Text wirklich lang genug ist."
        assert article_data[2] == "June 1, 2024"

    def test_prepemds_base_url_for_relative_links(self):
        ARTICLE_HTML_RELATIVE_LINK = """
        <html><body>
            <h1 class="entry-title">Artikel mit relativen Link</h1>
            <time datetime="2024-06-01">June 1, 2024</time>
            <div itemprop="articleBody">
                <p>Dies ist ein Artikel mit einem relativen Link, der ausreichend Text enthält um den Mindestzeichentest zu bestehen.</p>
            </div>
        </body></html>"""
        mock_request = make_mock_request(ARTICLE_HTML_RELATIVE_LINK)
        article_data, error_message = scrape_article("/test-relative-link", article_request=mock_request)
        assert error_message == ""
        assert article_data[1] == "https://theconversation.com/test-relative-link"
    
    def test_returns_error_on_bad_status_code(self):
        mock = make_mock_request(self.article_html_ok, status_code=404)
        article_data, error_message = scrape_article("https://theconversation.com/test-article", article_request=mock)
        assert article_data is None
        assert "Keine Antwort. Status Code: 404" in error_message

    def test_returns_error_when_article_request_fails(self):
        with patch("src.scraper.scraper_theconversation.requests.get", side_effect=requests.RequestException("network down")):
            article_data, error_message = scrape_article("https://theconversation.com/test-article")
        assert article_data is None
        assert "Fehler beim Abrufen des Artikels" in error_message

    def test_returns_none_when_article_has_no_headline(self):
        ARTICLE_HTML_MISSING_HEADLINE = """
        <html><body>
            <time datetime="2024-06-01">June 1, 2024</time>
            <div itemprop="articleBody">
                <p>Dies ist ein Artikel ohne Überschrift, aber mit ausreichend Text für den Test.</p>
            </div>
        </body></html>"""
        mock_request = make_mock_request(ARTICLE_HTML_MISSING_HEADLINE)
        article_data, error_message = scrape_article("https://theconversation.com/test-article", article_request=mock_request)
        assert article_data is None
        assert "Keine Überschrift gefunden" in error_message
    
    def test_returns_none_when_article_has_no_article_body(self):
        ARTICLE_HTML_MISSING_ARTICLE_BODY = """
        <html><body>
            <h1 class="entry-title">Artikel ohne Artikeltext</h1>
            <time datetime="2024-06-01">June 1, 2024</time>
        </body></html>"""
        mock_request = make_mock_request(ARTICLE_HTML_MISSING_ARTICLE_BODY)
        article_data, error_message = scrape_article("https://theconversation.com/test-article", article_request=mock_request)
        assert article_data is None
        assert "Keine Artikeltext gefunden" in error_message
    
    def test_rejects_non_theconversation_links(self):
        article_data, error_message = scrape_article("https://www.tagesschau.de/some-article")
        assert article_data is None
        assert "Ungültiger URL, überspringe Artikel: https://www.tagesschau.de/some-article.\n" in error_message

    def test_rejects_other_domains_with_mock(self):
        mock_request = make_mock_request(self.article_html_ok)
        article_data, error_message = scrape_article("https://www.tagesschau.de/some-article", article_request=mock_request)
        assert article_data is None
        assert "Ungültiger URL, überspringe Artikel: https://www.tagesschau.de/some-article.\n" in error_message
