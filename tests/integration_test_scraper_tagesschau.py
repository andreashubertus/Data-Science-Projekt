import pytest
import requests
from bs4 import BeautifulSoup
from scraper_tagesschau import (
    scrape_tagesschau_landing_page,
    get_article_headline,
    get_article_text,
    get_article_date,
    scrape_article,
    headers
)
 

class Test_Tagesschau_Landing_page:
    def test_tagesschau_reachable(self):
        links, error = scrape_tagesschau_landing_page()
        assert links is not None

    def test_landingpage_has_links(self):
        links, error = scrape_tagesschau_landing_page()
        assert links is not None
        assert len(links) > 0, (
            "Keine Artikel-Links gefunden - CSS-Selektor 'a.teaser__link' "
            "hat sich möglicherweise geändert."
        )

    def test_links_are_tagesschau_links(self):
        links, error = scrape_tagesschau_landing_page()
        assert links is not None, f"Fehler: {error}"
        for link in links:
            assert "tagesschau.de" in link or link.startswith("/"), f"Unerwarteter Link: {link}"

    def test_no_podcast_link_found(self):
        links, error = scrape_tagesschau_landing_page()
        assert links is not None, f"Fehler: {error}"
        for link in links:
            assert "/multimedia/podcast/" not in link, (
                f"Podcast-Link wurde nicht herausgefiltert: {link}"
            )
    


class TestTagesschauArtikelIntegration:
 
    @pytest.fixture(scope="class")
    def first_article_link(self):
        links, error = scrape_tagesschau_landing_page()
        assert links is not None, f"Startseite nicht erreichbar: {error}"
        link = links[0]
        if link.startswith("/"):
            link = "https://www.tagesschau.de" + link
        return link
 
    @pytest.fixture(scope="class")
    def real_article_soup(self, first_article_link):
        response = requests.get(first_article_link, headers=headers)
        assert response.status_code == 200, (
            f"Artikel nicht erreichbar (Status {response.status_code}): {first_article_link}"
        )
        return BeautifulSoup(response.text, "html.parser")
 
    def test_article_has_headline(self, real_article_soup, first_article_link):
        headline, error, issues = get_article_headline(real_article_soup, first_article_link, "", 0)
        assert headline is not None, (
            f"Überschrift nicht gefunden – Selektor 'article-head__headline--text' "
            f"hat sich möglicherweise geändert.\nFehler: {error}"
        )
        assert len(headline) > 0, "Überschrift ist leer."
 
    def test_article_has_text(self, real_article_soup, first_article_link):
        text, error, issues = get_article_text(real_article_soup, first_article_link, "", 0)
        assert issues == 0, (
            f"Artikeltext nicht gefunden – CSS-Selektor 'p.textabsatz' "
            f"hat sich möglicherweise geändert.\nFehler: {error}"
        )
        assert len(text) > 50, "Artikeltext zu kurz – möglicherweise wurde nur Teilinhalt extrahiert."
 
    def test_article_has_date(self, real_article_soup, first_article_link):
        date, error, issues = get_article_date(real_article_soup, first_article_link, "", 0)
        assert issues == 0, (
            f"Datum nicht gefunden – Selektor 'metatextline' "
            f"hat sich möglicherweise geändert.\nFehler: {error}"
        )
        assert len(date) > 0, "Datum ist leer."
 
    def test_article_everything_found(self, first_article_link):
        article_data, error = scrape_article(first_article_link)
        assert article_data is not None, (
            f"Artikel konnte nicht vollständig gescrapt werden.\n"
            f"Fehler: {error}\n"
            f"Tipp: Überprüfe die CSS-Selektoren in scraper_tagesschau.py"
        )
        assert article_data[0] is not None, "Headline fehlt."
        assert article_data[1] == first_article_link, "Link stimmt nicht überein."
        assert article_data[2] is not None, "Datum fehlt."
        assert len(article_data[3]) > 50, "Artikeltext zu kurz."
        assert article_data[4] is not None, "Scrape-Zeitstempel fehlt."