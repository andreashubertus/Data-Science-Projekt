import requests
from bs4 import BeautifulSoup
from datetime import datetime

def scrape_tagesschau_landing_page():
    url = "https://www.tagesschau.de/"
    request = requests.get(url)
    if request.status_code != 200:
        print(f"Keine Antwort von der Tagesschau-Website. Status Code: {request.status_code}")
        return None
    soup = BeautifulSoup(request.content, 'html.parser')
    articles = soup.find_all('a', class_='teaser__link')

    articles_link_list = [article.get('href') for article in articles if article.get('href')]

    return articles_link_list


def scrape_article(link):
    if not link.startswith("http"):
        link = "https://www.tagesschau.de" + link
    article_request = requests.get(link)
    
    if article_request.status_code != 200:
        print(f"Keine Antwort von der Artikel-Website. Status Code: {article_request.status_code}")
        return None
    try:
        article_soup = BeautifulSoup(article_request.text, "html.parser")
        article_headline = article_soup.find(class_ = "article-head__headline--text").get_text(separator= " ",strip=True)
        article = article_soup.find_all("p", class_="textabsatz")
        date = article_soup.find(class_ = "metatextline")
    except AttributeError as e:
        print(f"Fehler beim Scrapen des Artikels: {e}")
        return None
    article_text = ""
    for p in article:
        article_text += f"\n {p.get_text(strip = True)}"
        if len(article_text) < 50:
            print("Artikeltext zu kurz, überspringe Artikel.")
            continue
    try:
        date = date.get_text(separator= " ",strip=True)
    except:
        date = "Kein Datum bezüglich des Standes des Artikels gefunden."
    
    return [article_headline, link, date, article_text, datetime.now().strftime("%Y-%m-%d %H:%M:%S")]

def scrape_tagesschau():
    articles = []
    articles_link = scrape_tagesschau_landing_page()
    if articles_link is None:
        print("Keine Artikel gefunden.")
        return []
    else:
        print(f"{len(articles_link)} Artikel gefunden. Beginne mit dem Scraping der Artikel...")
        pass
        for link in articles_link:
            articles.append(scrape_article(link))
    for article in articles:
        if article is not None:
            print(f"Artikel: {article[0]}\nLink: {article[1]}\nDatum: {article[2]}\nText: {article[3][:200]}...\nScraped am: {article[4]}\n")



if __name__ == "__main__":
    print(scrape_tagesschau())