import pytest
import requests
from bs4 import BeautifulSoup
from src.scraper.scraper_theconversation import (
    get_links_from_theconversation_rss,
    get_article_headline,
    get_article_text,
    get_article_date,
    scrape_article,
    headers
)


class TestRssFeedIntegration:

    def test_rss_reachable(self):
        links, error = get_links_from_theconversation_rss()
        assert links is not None, f"RSS-Feed nicht erreichbar: {error}"
        assert error == ""

    def test_rss_has_links(self):
        links, error = get_links_from_theconversation_rss()
        assert links is not None, f"Fehler: {error}"
        assert len(links) > 0, "RSS-Feed enthält keine Artikel-Links - Struktur hat sich möglicherweise geändert."

    def test_rss_links_all_theconversation(self):
        links, error = get_links_from_theconversation_rss()
        assert links is not None, f"Fehler: {error}"
        for link in links:
            assert "theconversation.com" in link, f"Unerwarteter Link im Feed: {link}"


class TestArtikelScrapingIntegration:

    @pytest.fixture(scope="class")
    def erster_artikel_link(self):
        links, error = get_links_from_theconversation_rss()
        assert links is not None, f"RSS-Feed nicht erreichbar: {error}"
        return links[0]

    @pytest.fixture(scope="class")
    def echter_artikel_soup(self, erster_artikel_link):
        response = requests.get(erster_artikel_link, headers=headers)
        assert response.status_code == 200, (
            f"Artikel nicht erreichbar (Status {response.status_code}): {erster_artikel_link}"
        )
        return BeautifulSoup(response.text, "html.parser")

    def test_article_has_headline(self, echter_artikel_soup, erster_artikel_link):
        headline, error, issues = get_article_headline(echter_artikel_soup, erster_artikel_link, "", 0)
        assert headline is not None, (
            f"Überschrift nicht gefunden – CSS-Selektor 'h1.entry-title' hat sich möglicherweise geändert.\n"
            f"Fehler: {error}"
        )
        assert len(headline) > 0, "Überschrift ist leer."

    def test_article_has_text(self, echter_artikel_soup, erster_artikel_link):
        text, error, issues = get_article_text(echter_artikel_soup, erster_artikel_link, "", 0)
        assert issues == 0, (
            f"Artikeltext nicht gefunden – CSS-Selektor 'div[itemprop=articleBody]' hat sich möglicherweise geändert.\n"
            f"Fehler: {error}"
        )
        assert len(text) > 50, "Artikeltext zu kurz – möglicherweise wurde nur Teilinhalt extrahiert."

    def test_article_has_date(self, echter_artikel_soup, erster_artikel_link):
        date, error, issues = get_article_date(echter_artikel_soup, erster_artikel_link, "", 0)
        assert issues == 0, (
            f"Datum nicht gefunden – 'time[datetime]' Selektor hat sich möglicherweise geändert.\n"
            f"Fehler: {error}"
        )
        assert len(date) > 0, "Datum ist leer."

    def test_article_found_all(self, erster_artikel_link):
        article_data, error = scrape_article(erster_artikel_link)
        assert article_data is not None, (
            f"Artikel konnte nicht vollständig gescrapt werden.\n"
            f"Fehler: {error}\n"
            f"Tipp: Überprüfe die CSS-Selektoren in scraper_theconversation.py"
        )
        assert article_data[0] is not None, "Headline fehlt."
        assert article_data[1] == erster_artikel_link, "Link stimmt nicht überein."
        assert article_data[2] is not None, "Datum fehlt."
        assert len(article_data[3]) > 50, "Artikeltext zu kurz."
        assert article_data[4] is not None, "Scrape-Zeitstempel fehlt."
