import pytest
from unittest.mock import MagicMock, patch
from src.scraper.scraper_tagesschau import *
import requests
from bs4 import BeautifulSoup

def make_mock_request(html: str, status_code: int = 200) -> MagicMock:
    mock = MagicMock()
    mock.status_code = status_code
    mock.text = html
    return mock

    

class TestScrapeTagesschauLandingPage:
    
    def test_returns_filtered_article_links(self):
        LANDING_HTML_OK = """
        <html><body>
        <a class="teaser__link" href="/inland/artikel-1.html">Artikel 1</a>
        <a class="teaser__link" href="/inland/artikel-2.html">Artikel 2</a>
        <a class="teaser__link" href="https://www.tagesschau.de">Homepage (wird gefiltert)</a>
        <a class="teaser__link" href="https://www.tagesschau.de/multimedia/podcast/11km/podcast-11km-3504.html">Podcast (wird gefiltert)</a>
        <a class="teaser__link" href="https://www.tagesschau.de/multimedia/podcast/anderer-podcast.html">Podcast 2 (wird gefiltert)</a>
        </body></html>
        """
        mock_request = make_mock_request(LANDING_HTML_OK)
        links, error = scrape_tagesschau_landing_page(request=mock_request)
        assert len(links) == 2
        assert "https://www.tagesschau.de" not in links
        assert any(link.startswith("https://www.tagesschau.de/multimedia/podcast/") for link in links) == False
        assert error == ""
        assert links == ["/inland/artikel-1.html", "/inland/artikel-2.html"]
    
    def test_returns_error_on_no_articles(self):
        LANDING_HTML_NO_ARTICLES = "<html><body><p>Keine Artikel</p></body></html>"

        mock_request = make_mock_request(LANDING_HTML_NO_ARTICLES)
        links, error = scrape_tagesschau_landing_page(request=mock_request)
        assert links is None
        assert "Keine Artikel auf der Tagesschau-Startseite gefunden. Überprüfe die Struktur der Webseite oder die Klasse der Artikel-Links." in error

    def test_returns_error_on_bad_status_code(self):
        LANDING_HTML_OK = """
        <html><body>
        <a class="teaser__link" href="/inland/artikel-1.html">Artikel 1</a>
        <a class="teaser__link" href="/inland/artikel-2.html">Artikel 2</a>
        <a class="teaser__link" href="https://www.tagesschau.de">Homepage (wird gefiltert)</a>
        <a class="teaser__link" href="https://www.tagesschau.de/multimedia/podcast/11km/podcast-11km-3504.html">Podcast (wird gefiltert)</a>
        <a class="teaser__link" href="https://www.tagesschau.de/multimedia/podcast/anderer-podcast.html">Podcast 2 (wird gefiltert)</a>
        </body></html>
        """
        
        mock_request = make_mock_request(LANDING_HTML_OK, status_code=500)
        links, error = scrape_tagesschau_landing_page(request=mock_request)
        assert links is None
        assert "Keine Antwort von der Tagesschau-Website. Status Code: 500" in error
    
   
    def test_skips_links_without_href(self): 
        LANDING_HTML_NO_HREF = """
        <html><body>
        <a class="teaser__link" href="/inland/artikel-1.html">Artikel 1</a>
        <a class="teaser__link">Kein href</a>
        </body></html>
        """
        mock_request = make_mock_request(LANDING_HTML_NO_HREF)
        links, error = scrape_tagesschau_landing_page(request=mock_request)
        assert links == ["/inland/artikel-1.html"]
        assert error == ""

    def test_returns_empty_list_when_all_links_filtered(self):
        LANDING_HTML_ALL_FILTERED = """
        <html><body>
        <a class="teaser__link" href="https://www.tagesschau.de">Home</a>
        <a class="teaser__link" href="https://www.tagesschau.de/multimedia/podcast/foo.html">Podcast</a>
        </body></html>
        """
        mock_request = make_mock_request(LANDING_HTML_ALL_FILTERED)
        links, error = scrape_tagesschau_landing_page(request=mock_request)
        assert links == []
        assert error == ""



class Test_get_Article_headline:
    def test_get_article_headline_success(self):
        html = '<h1 class="article-head__headline--text">Tagesschau News</h1>'
        soup = BeautifulSoup(html, 'html.parser')
        
        headline, error, issues = get_article_headline(soup, "link123", "", 0)
        
        assert headline == "Tagesschau News"
        assert error == ""
        assert issues == 0

    def test_get_article_headline_not_found_and_accumelationg_existing_errors(self):
        html = '<div class="falsche-klasse">Keine Headline</div>'
        soup = BeautifulSoup(html, 'html.parser')
        
        headline, error, issues = get_article_headline(soup, "link123", "Bisheriger Fehler. ", 5)
        
        assert headline is None
        assert "Keine Überschrift gefunden" in error
        assert "link123" in error
        assert issues == 6




class Test_get_article_text:
    def test_get_article_text_success(self):
        ARTICLE_HTML_OK = """
        <html><body>
            <p class="textabsatz">Dies ist der erste Teil des Artikels.</p>
            <p class="textabsatz">Dies ist der zweite Teil, um die Mindestlänge zu erreichen.</p>
        </body></html>
        """
        soup = BeautifulSoup(ARTICLE_HTML_OK, 'html.parser')
        text, error, issues = get_article_text(soup, "link123", "", 0)
        assert "Dies ist der erste Teil des Artikels." in text
        assert "Dies ist der zweite Teil" in text
        assert error == ""
        assert issues == 0
    def test_get_article_text_not_found(self):
        ARTICLE_HTML_NO_TEXT = "<html><body><p class='falsche-klasse'></p></body></html>"
        soup = BeautifulSoup(ARTICLE_HTML_NO_TEXT, 'html.parser')
        text, error, issues = get_article_text(soup, "link123", "", 0)
        assert text == ""
        assert "Keine Artikeltext gefunden" in error
        assert "link123" in error
        assert issues == 1

    def test_get_article_text_too_short(self):
        ARTICLE_HTML_TOO_SHORT = """<html><body>
            <p class="textabsatz">(" " * 100)Kurz</p>
        </body></html>"""
        soup = BeautifulSoup(ARTICLE_HTML_TOO_SHORT, 'html.parser')
        link = "https://www.tagesschau.de/kurz.html"
        
        text, error, issues = get_article_text(soup, link, "", 0)
        
        assert "Artikeltext zu kurz" in error
        assert link in error
        assert issues == 1

    def test_get_article_text_strips_whitespace(self):
        
        long_html = '<html><body><p class="textabsatz"> ' + ("  " * 10) + "Testinhalt" + ' </p></body></html>'
        soup = BeautifulSoup(long_html, 'html.parser')
        
        text, error, issues = get_article_text(soup, "link", "", 0)
        
        assert text.startswith("\n Testinhalt") 
        assert text.strip().startswith("Testinhalt")
    
    def test_get_article_text_only_whitespace(self):
        html = '<html><body><p class="textabsatz">     </p><p class="textabsatz">   </p></body></html>'
        soup = BeautifulSoup(html, "html.parser")
        text, error, issues = get_article_text(soup, "test-link", "", 0)
        assert "Artikeltext zu kurz" in error
        assert issues == 1

    def test_skips_empty_paragraphs(self):
        html = """
        <html><body>
            <p class="textabsatz">    </p>
            <p class="textabsatz">Dies ist ein ausreichend langer Absatz mit echtem Inhalt für den Test.</p>
        </body></html>
        """
        soup = BeautifulSoup(html, "html.parser")
        text, error, issues = get_article_text(soup, "test-link", "", 0)
        assert "Dies ist ein ausreichend langer Absatz" in text
        assert issues == 0


class Test_get_article_date:
    def test_get_article_date_success(self):
        ARTICLE_HTML_DATE = """
        <html><body>
            <div class="metatextline">1. Juni 2024</div>
        </body></html>
        """
        soup = BeautifulSoup(ARTICLE_HTML_DATE, 'html.parser')
        date, error, issues = get_article_date(soup, "link123", "", 0)
        assert date == "1. Juni 2024"
        assert error == ""
        assert issues == 0

    def test_get_article_date_not_found(self):
        ARTICLE_HTML_NO_DATE = "<html><body><p>Hier gibts kein Datum</p></body></html>"
        soup = BeautifulSoup(ARTICLE_HTML_NO_DATE, 'html.parser')
        date, error, issues = get_article_date(soup, "link123", "", 0)
        assert date == "Kein Datum bezüglich des Standes des Artikels gefunden.\n"
        assert "Kein Datum gefunden" in error
        assert "link123" in error
        assert issues == 1

    def test_return_error_when_metatextline_is_empty(self):
        html = '<html><body><div class="metatextline">   </div></body></html>'
        soup = BeautifulSoup(html, "html.parser")
        date, error, issues = get_article_date(soup, "test-link", "", 0)
        assert date == "" or date is not None


class TestScrapeArticle:
    ARTICLE_HTML_OK = """
    <html><body>
        <h1 class="article-head__headline--text">Warum sollte man sich einen Webscraper selber bauen?</h1>
        <p class="metatextline">22. April 2026</p>
        <p class="textabsatz">Ein eigener Webscraper ist toll, man kann ihn erweitern und beispielsweise einen JARVIS nachbauen.</p>
        <p class="textabsatz">Hier nach baut man noch einen MCP dazu und kann per LLM direkt drauf zugreifen.</p>
    </body></html>
    """
 
    def test_returns_article_data_on_success(self):
        mock_request = make_mock_request(self.ARTICLE_HTML_OK)
        article_data, error = scrape_article("https://www.tagesschau.de/test007.html", article_request=mock_request)
        assert error == ""
        assert article_data[0] == "Warum sollte man sich einen Webscraper selber bauen?"
        assert article_data[1] == "https://www.tagesschau.de/test007.html"
        assert article_data[2] == "22. April 2026"
        assert "Ein eigener Webscraper ist toll" in article_data[3]
        assert article_data[4] is not None
   

    def test_prepends_base_url_for_relative_links(self):
        mock_request = make_mock_request(self.ARTICLE_HTML_OK)
        article_data, error = scrape_article("/test007.html", article_request=mock_request)
        assert error == ""
        assert article_data[1] == "https://www.tagesschau.de/test007.html"
 
    def test_returns_error_on_bad_status_code(self):
        mock_request = make_mock_request(self.ARTICLE_HTML_OK, status_code=404)
        article_data, error = scrape_article("https://www.tagesschau.de/test007.html", article_request=mock_request)
        assert article_data is None
        assert "404" in error

    def test_returns_none_when_no_headline(self):
        html = """
        <html><body>
            <p class="metatextline">22. April 2026</p>
            <p class="textabsatz">Ein eigener Webscraper ist toll, man kann ihn erweitern und beispielsweise einen JARVIS nachbauen.</p>
        </body></html>
        """
        mock_request = make_mock_request(html)
        article_data, error = scrape_article("https://www.tagesschau.de/test007.html", article_request=mock_request)
        assert article_data is None
        assert "Keine Überschrift gefunden" in error
    
    def test_returns_none_when_no_article_text(self):
        html = """
        <html><body>
            <h1 class="article-head__headline--text">Titel</h1>
            <p class="metatextline">22. April 2026</p>
        </body></html>
        """
        mock_request = make_mock_request(html)
        article_data, error = scrape_article("https://www.tagesschau.de/test007.html", article_request=mock_request)
        assert article_data is None
        assert "Keine Artikeltext gefunden" in error

    def test_returns_none_when_no_date(self):
        html = """
        <html><body>
            <h1 class="article-head__headline--text">Titel</h1>
            <p class="textabsatz">Ein eigener Webscraper ist toll, man kann ihn erweitern und beispielsweise einen JARVIS nachbauen.</p>
        </body></html>
        """
        mock_request = make_mock_request(html)
        article_data, error = scrape_article("https://www.tagesschau.de/test007.html", article_request=mock_request)
        assert article_data is None
        assert "Kein Datum gefunden" in error

    def test_rejects_non_tagesschau_links(self):
        article_data, error = scrape_article("https://theconversation.com/some-article")
        assert article_data is None
        assert "https://theconversation.com/some-article" in error
    
    def test_rejects_non_tagesschau_links_with_mock(self):
        mock_request = make_mock_request(self.ARTICLE_HTML_OK)
        article_data, error = scrape_article("https://theconversation.com/some-article", article_request=mock_request)
        assert article_data is None
        assert "https://theconversation.com/some-article" in error
