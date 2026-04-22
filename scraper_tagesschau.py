import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time


headers = {
    'User-Agent': 'DHBW Data science student - Web Scraping for educational purposes)'
}




def scrape_tagesschau_landing_page():
    url = "https://www.tagesschau.de/"
    request = requests.get(url, headers=headers)
    if request.status_code != 200:
        print(f"Keine Antwort von der Tagesschau-Website. Status Code: {request.status_code}")
        return None
    soup = BeautifulSoup(request.content, 'html.parser')
    articles = soup.find_all('a', class_='teaser__link')
    if articles == []:
        print("Keine Artikel auf der Tagesschau-Startseite gefunden. Überprüfe die Struktur der Webseite oder die Klasse der Artikel-Links.")
        return None

    articles_link_list = [article.get('href') for article in articles if article.get('href')]

    return articles_link_list


def scrape_article(link):
    if not link.startswith("http"):
        link = "https://www.tagesschau.de" + link
    article_request = requests.get(link, headers=headers)
    
    if article_request.status_code != 200:
        print(f"Keine Antwort von der Artikel-Website. Status Code: {article_request.status_code}")
        return None
    try:
        found_issues = 0
        article_soup = BeautifulSoup(article_request.text, "html.parser")
        article_headline = article_soup.find(class_ = "article-head__headline--text").get_text(separator= " ",strip=True)
        if article_headline is None:
            print(f"Keine Überschrift gefunden, überspringe Artikel: {link}.")
            found_issues += 1
        article = article_soup.find_all("p", class_="textabsatz")
        if article is None:
            print(f"Keine Artikeltext gefunden, überspringe Artikel: {link}.")
            found_issues += 1

        date = article_soup.find(class_ = "metatextline")
        if date is None:
            print(f"Kein Datum gefunden, überspringe Artikel: {link}.")
            found_issues += 1
        if found_issues > 0:
            print(f"Artikel hat {found_issues} fehlende Elemente, überspringe Artikel: {link}. Falls dies häufig vorkommt, überprüfe die Struktur der Webseite.")
            return None

    except AttributeError as e:
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
            time.sleep(2)
    return articles






if __name__ == "__main__":
    print("Starte Tagesschau Scraping")
    tagesschau_articles = scrape_tagesschau()

    # for article in tagesschau_articles:
    #     if article is not None:
    #         print(f"Headline: {article[0]}")
    #         print(f"Link: {article[1]}")
    #         print(f"Datum: {article[2]}")
    #         print(f"Artikeltext: {article[3][:200]}...")
    #         print(f"Scraped am: {article[4]}")
    #         print("-" * 80)