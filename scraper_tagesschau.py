import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time


headers = {
    'User-Agent': 'DHBW Data science student - Web Scraping for educational purposes)'
}


def is_valid_link(url):
    exclude_list = [
        "https://www.tagesschau.de",
        "/wetter/regenradar-deutschland"
    ]
    if not url or url in exclude_list:
        return False
    if url.startswith("https://www.tagesschau.de/multimedia/podcast/"):
        return False
    return True




def scrape_tagesschau_landing_page(request = None):
    errormessage = ""
    url = "https://www.tagesschau.de/"
    if request is None:
        request = requests.get(url, headers=headers)
    
    if request.status_code != 200:
        errormessage += f"Keine Antwort von der Tagesschau-Website. Status Code: {request.status_code}"
        return None, errormessage
    
    soup = BeautifulSoup(request.text, 'html.parser')
    articles = soup.find_all('a', class_='teaser__link')
    if articles == []:
        errormessage += "Keine Artikel auf der Tagesschau-Startseite gefunden. Überprüfe die Struktur der Webseite oder die Klasse der Artikel-Links."
        return None,errormessage

    articles_link_list = [a.get('href') for a in articles if is_valid_link(a.get('href'))]

    return articles_link_list, errormessage


def get_article_headline(article_soup, link, errormessage, found_issues):
    article_headline = article_soup.find(class_ = "article-head__headline--text")
    if article_headline is None:
        errormessage += f"Keine Überschrift gefunden, überspringe Artikel: {link}.\n"
        found_issues += 1
    else:
        article_headline = article_headline.get_text(separator= " ",strip=True)
    return article_headline, errormessage, found_issues

def get_article_text(article_soup, link, errormessage, found_issues):
    article = article_soup.find_all("p", class_="textabsatz")
    if article is None or article == []:
        errormessage += f"Keine Artikeltext gefunden, überspringe Artikel: {link}.\n"
        found_issues += 1
        article_text = ""
    
    else:
        article_text = ""
        for p in article:
            article_text += f"\n {p.get_text(strip = True)}"
        if len(article_text) < 50:
            errormessage += f"Artikeltext zu kurz, überspringe Artikel: {link}.\n"
            found_issues += 1
    return article_text, errormessage, found_issues


def get_article_date(article_soup, link, errormessage, found_issues):
    date = article_soup.find(class_ = "metatextline")
    if date is None:
        errormessage += f"Kein Datum gefunden, überspringe Artikel: {link}.\n"
        found_issues += 1
    try:
        article_date = date.get_text(separator= " ",strip=True)
    except:
        article_date = "Kein Datum bezüglich des Standes des Artikels gefunden.\n"
    return article_date, errormessage, found_issues

def scrape_article(link, article_request = None):
    errormessage = ""
    if not link.startswith("http"):
        link = "https://www.tagesschau.de" + link
    if article_request is None:
        article_request = requests.get(link, headers=headers)     
        if article_request.status_code != 200:
            errormessage += f"Keine Antwort von der Artikel-Website. Status Code: {article_request.status_code}\n"
            return None, errormessage
    try:
        found_issues = 0
        article_soup = BeautifulSoup(article_request.text, "html.parser")
        
        article_headline, errormessage, found_issues = get_article_headline(article_soup, link, errormessage, found_issues)

        
        article_text ,errormessage, found_issues = get_article_text(article_soup, link, errormessage, found_issues)

        article_date , errormessage, found_issues = get_article_date(article_soup, link, errormessage, found_issues)

        if found_issues > 0:
            errormessage += f"Artikel hat {found_issues} fehlende Elemente, überspringe Artikel: {link}. Falls dies häufig vorkommt, überprüfe die Struktur der Webseite."
            return None, errormessage
    except Exception as e:
        errormessage += f"Fehler beim Scrapen des Artikels: {e}, link: {link}"
        return None, errormessage
    
    return [article_headline, link, article_date, article_text, datetime.now().strftime("%Y-%m-%d %H:%M:%S")],errormessage

def scrape_tagesschau():
    articles = []
    articles_link, error = scrape_tagesschau_landing_page()
    if articles_link is None:
        print(error)
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
        if article[0] is not None:
            print(f"Headline: {article[0][0]}")
            print(f"Link: {article[0][1]}")
            print(f"Datum: {article[0][2]}")
            print(f"Artikeltext: {article[0][3][:200]}...")
            print(f"Scraped am: {article[0][4]}")
            print("-" * 80)
        else:
            print(f"Fehler: {article[1]}")
            print("\n" + "-" * 80)