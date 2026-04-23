import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time


headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    


def get_links_from_theconversation_rss(request=None):
    errormessage = ""
    rss_url = "https://theconversation.com/global/articles.atom"

    if request is None:
        request = requests.get(rss_url, headers=headers)
    if request.status_code != 200:
        errormessage += f"Keine Antwort vom TheConversation RSS-Feed. Status Code: {request.status_code}"
        return None, errormessage
    soup = BeautifulSoup(request.content, "xml")
    links = [link['href'] for link in soup.find_all('link') if 'rel' in link.attrs and link['rel'] == 'alternate' and link['href'] not in ["https://theconversation.com"]]
    
    if not links:
        errormessage += "Keine Artikel im TheConversation RSS-Feed gefunden. Überprüfe die Struktur des Feeds."
        return None, errormessage
    return links, errormessage


def get_article_headline(article_soup, link, errormessage, found_issues):
    article_headline = article_soup.find("h1", class_="entry-title")
    if article_headline is None:
        errormessage += f"Keine Überschrift gefunden, überspringe Artikel: {link}.\n"
        found_issues += 1
    else:
        article_headline = article_headline.get_text(separator=" ", strip=True)
    return article_headline, errormessage, found_issues


def get_article_text(article_soup, link, errormessage, found_issues):
    content_div = article_soup.find("div", itemprop="articleBody")
    if content_div is None:
        errormessage += f"Keine Artikeltext gefunden, überspringe Artikel: {link}.\n"
        found_issues += 1
        return "", errormessage, found_issues

    paragraphs = content_div.find_all("p")
    if not paragraphs:
        errormessage += f"Keine Absätze gefunden, überspringe Artikel: {link}.\n"
        found_issues += 1
        return "", errormessage, found_issues

    article_text = ""
    for p in paragraphs:
        text = p.get_text(strip=True)
        if text:
            article_text += f"\n{text}"

    if len(article_text) < 50:
        errormessage += f"Artikeltext zu kurz, überspringe Artikel: {link}.\n"
        found_issues += 1

    return article_text, errormessage, found_issues


def get_article_date(article_soup, link, errormessage, found_issues):
    date_element = article_soup.find("time")
    if date_element is None or not date_element.has_attr('datetime'):
        errormessage += f"Kein Datum gefunden, überspringe Artikel: {link}.\n"
        found_issues += 1
        return "Kein Datum gefunden.\n", errormessage, found_issues

    article_date = date_element.get_text(strip=True)
    return article_date, errormessage, found_issues


def scrape_article(link , article_request = None):
    error_message = ""

    if not link.startswith("http"):
        link = "https://theconversation.com" + link
    if article_request is None:
        article_request = requests.get(link, headers=headers)
        if article_request.status_code != 200:
            print(f"Keine Antwort. Status Code: {article_request.status_code}")
      
    try:
        found_issues = 0
        article_soup = BeautifulSoup(article_request.text, "html.parser")

        article_headline, error_message, found_issues = get_article_headline(article_soup, link, error_message, found_issues)
        article_text, error_message, found_issues = get_article_text(article_soup, link, error_message, found_issues)
        article_date, error_message, found_issues = get_article_date(article_soup, link, error_message, found_issues)

        
        if found_issues > 0:
            print(f"{error_message}Artikel hat {found_issues} fehlende Elemente, überspringe Artikel: {link}.\nFalls dies häufig vorkommt, überprüfe die Struktur der Webseite.\n")
            return None
        
    except Exception as e:
        errormessage += f"Fehler beim Scrapen des Artikels: {e}, link: {link}"
        return None,error_message

    return [
        article_headline, 
        link, 
        article_date, 
        article_text.strip(), 
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ]
        
    


def scrape_theconversation():
    articles = []
    articles_link, error_message = get_links_from_theconversation_rss()
    articles_link = articles_link
    if articles_link is None:
        print(error_message)
        return []
    else:
        for link in articles_link:
            articles.append(scrape_article(link))
            #time.sleep(2)
    return articles, error_message


if __name__ == "__main__":
    print("Starte The Conversation Scraping")
    theconversation_articles,error_message = scrape_theconversation()
    print("The Conversation abgeschlossen")
    if error_message:
        print(f"Fehlermeldungen: {error_message}")
    for article in theconversation_articles:
        if article is not None:
            print(f"Headline: {article[0]}")
            print(f"Link: {article[1]}")
            print(f"Datum: {article[2]}")
            print(f"Artikeltext: {article[3][:200]}...")
            print(f"Scraped am: {article[4]}")
            print("-" * 80)