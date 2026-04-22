import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time


headers = {
    'User-Agent': 'DHBW Data science student - Web Scraping for educational purposes)'
}




def scrape_tagesschau_landing_page(request = None):
    url = "https://www.tagesschau.de/"
    if request is None:
        request = requests.get(url, headers=headers)
        if request.status_code != 200:
            print(f"Keine Antwort von der Tagesschau-Website. Status Code: {request.status_code}")
            return None
    soup = BeautifulSoup(request.text, 'html.parser')
    articles = soup.find_all('a', class_='teaser__link')
    if articles == []:
        print("Keine Artikel auf der Tagesschau-Startseite gefunden. Überprüfe die Struktur der Webseite oder die Klasse der Artikel-Links.")
        return None

    articles_link_list = [article.get('href') for article in articles if article.get('href') and article.get('href') not in ["https://www.tagesschau.de","https://www.tagesschau.de/multimedia/podcast/11km/podcast-11km-3504.html"] and not article.get('href').startswith("https://www.tagesschau.de/multimedia/podcast/")]

    return articles_link_list


def scrape_article(link, article_request = None):
    if not link.startswith("http"):
        link = "https://www.tagesschau.de" + link
    if article_request is None:
        article_request = requests.get(link, headers=headers)     
        if article_request.status_code != 200:
            print(f"Keine Antwort von der Artikel-Website. Status Code: {article_request.status_code}")
            return None
    try:
        found_issues = 0
        article_soup = BeautifulSoup(article_request.text, "html.parser")
        article_headline = article_soup.find(class_ = "article-head__headline--text")
        if article_headline is None:
            print(f"Keine Überschrift gefunden, überspringe Artikel: {link}.")
            found_issues += 1
        else:
            article_headline = article_headline.get_text(separator= " ",strip=True)
        article = article_soup.find_all("p", class_="textabsatz")
        if article is None or article == []:
            print(f"Keine Artikeltext gefunden, überspringe Artikel: {link}.")
            found_issues += 1

        date = article_soup.find(class_ = "metatextline")
        if date is None:
            print(f"Kein Datum gefunden, überspringe Artikel: {link}.")
            found_issues += 1
        if found_issues > 0:
            print(f"Artikel hat {found_issues} fehlende Elemente, überspringe Artikel: {link}. Falls dies häufig vorkommt, überprüfe die Struktur der Webseite.")
            return None

    except Exception as e:
        print(f"Fehler beim Scrapen des Artikels: {e}, link: {link}")
        return None
    article_text = ""
    for p in article:
        article_text += f"\n {p.get_text(strip = True)}"
    if len(article_text) < 50:
        print(f"Artikeltext zu kurz, überspringe Artikel: {link}.")
        return None
    try:
        date = date.get_text(separator= " ",strip=True)
    except:
        date = "Kein Datum bezüglich des Standes des Artikels gefunden. "
    
    return [article_headline, link, date, article_text, datetime.now().strftime("%Y-%m-%d %H:%M:%S")]

def scrape_tagesschau():
    articles = []
    articles_link = scrape_tagesschau_landing_page()
    if articles_link is None:
        print("Keine Artikel gefunden.")
        return []
    else:
        for link in articles_link:
            articles.append(scrape_article(link))
            #time.sleep(2)
    return articles






if __name__ == "__main__":
    print("Starte Tagesschau Scraping")
    tagesschau_articles = scrape_tagesschau()
    print("Tagesschau abgeschlossen")
    for article in tagesschau_articles:
        if article is not None:
            print(f"Headline: {article[0]}")
            print(f"Link: {article[1]}")
            print(f"Datum: {article[2]}")
            print(f"Artikeltext: {article[3][:200]}...")
            print(f"Scraped am: {article[4]}")
            print("-" * 80)