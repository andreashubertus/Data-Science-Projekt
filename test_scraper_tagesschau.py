import scraper_tagesschau

def test_scrape_tagesschau_landing_page():
    print("Teste scrape_tagesschau_landing_page mit Mock-Daten")
    mock_html = """
    <body>
            <a class="teaser__link" href="https://www.tagesschau.de/test-artikel-100.html">
                Hier steht der Titel des Artikels
            </a>
            <a class="teaser__link" href="https://www.tagesschau.de/test-artikel-200.html">
                Ein zweiter Artikel
            </a>
        </body>
    """

    class MockResponse:
        def __init__(self, text, status_code):
            self.text = text
            self.status_code = status_code

    mock_res = MockResponse(text=mock_html, status_code=200)
    ergebnis = scraper_tagesschau.scrape_tagesschau_landing_page(request=mock_res)
    if ergebnis is not None:
        assert len(ergebnis) == 2, f"Erwartet 2 Artikel-Links, aber {len(ergebnis)} gefunden."
        assert ergebnis[0] == "https://www.tagesschau.de/test-artikel-100.html", f"Erster Link unerwartet: {ergebnis[0]}"
        assert ergebnis[1] == "https://www.tagesschau.de/test-artikel-200.html", f"Zweiter Link unerwartet: {ergebnis[1]}"
        print("Test scrape_tagesschau_landing_page mit Mock-Daten erfolgreich.")

    else:
        print("Test scrape_tagesschau_landing_page mit Mock-Daten fehlgeschlagen: Kein Ergebnis zurückgegeben.")



def test_scrape_article():
    print("Teste scrape_article mit Mock-Daten")
    mock_html = """
    <html>
        <body>
            <h1 class="article-head__headline--text">Warum sollte man sich einen Webscraper selber bauen?</h1>
            <p class="metatextline">22. April 2026</p>
            <p class="textabsatz">Ein eigener Webscraper ist toll man kann ihn erweitern und Beispielsweise einen JARVIS oder eine Friday aus Ironman nachbauen.</p>
            <p class="textabsatz">Hier nach baut man noch nen MCP dazu und kann per LLM direkt drauf zugreifen.</p>
        </body>
    </html>
    """
    class MockResponse:
        def __init__(self, text, status_code):
            self.text = text
            self.status_code = status_code

    fake_link = "https://www.tagesschau.de/test007.html"
    mock_res = MockResponse(text=mock_html, status_code=200)
    ergebnis = scraper_tagesschau.scrape_article(fake_link, article_request=mock_res)
    if ergebnis is not None:
        assert ergebnis[0] == "Warum sollte man sich einen Webscraper selber bauen?", f"Unerwartete Überschrift: {ergebnis[0]}"
        assert ergebnis[1] == fake_link, f"Unerwarteter Link: {ergebnis[1]}"
        assert ergebnis[2] == "22. April 2026", f"Unerwartetes Datum: {ergebnis[2]}"
        assert ergebnis[3].strip().startswith("Ein eigener Webscraper ist toll"), f"Unerwarteter Artikeltext: {ergebnis[3][:50]}"
        print("Test scrape_article mit Mock-Daten erfolgreich.")

    else:
        print("Test scrape_article mit Mock-Daten fehlgeschlagen: Kein Ergebnis zurückgegeben.")


if __name__ == "__main__":
    test_scrape_tagesschau_landing_page()
    test_scrape_article()