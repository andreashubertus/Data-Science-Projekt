import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time


headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    


def get_links_from_theconversation_rss():
    rss_url = "https://theconversation.com/global/articles.atom"
    request = requests.get(rss_url, headers=headers)
    soup = BeautifulSoup(request.content, "xml")
    links = [link['href'] for link in soup.find_all('link') if 'rel' in link.attrs and link['rel'] == 'alternate' and link['href'] not in ["https://theconversation.com"]]
    
    return links


def scrape_article(link , article_request = None):
    if not link.startswith("http"):
        link = "https://theconversation.com" + link
    if article_request is None:
        article_request = requests.get(link, headers=headers)
        if article_request.status_code != 200:
            print(f"Keine Antwort. Status Code: {article_request.status_code}")
      
    try:
        found_issues = 0
        error_messages = f""
        article_soup = BeautifulSoup(article_request.text, "html.parser")

        article_headline = article_soup.find("h1", class_="entry-title")
        if article_headline is None:
            error_messages += f"Keine Überschrift gefunden.\n"
            found_issues += 1
        else:
            article_headline = article_headline.get_text(separator=" ", strip=True)

        content_div = article_soup.find("div", itemprop="articleBody")
        if content_div is None:
            error_messages += f"Kein Artikeltext gefunden.\n"
            found_issues += 1
        else:
            article_paragraphs = content_div.find_all("p") if content_div else None
            if article_paragraphs == None:
                error_messages += f"Keine Absätze gefunden.\n"
                found_issues += 1
        date_element = article_soup.find("time")
        if date_element and date_element.has_attr('datetime'):
            date = date_element.get_text(strip=True)
        else:
            date = f"Kein Datum gefunden."

        if found_issues > 0:
            print(f"{error_messages}Artikel hat {found_issues} fehlende Elemente, überspringe Artikel: {link}.\nFalls dies häufig vorkommt, überprüfe die Struktur der Webseite.\n")
            return None
        
    except Exception as e:
        print(f"Fehler beim Scrapen des Artikels: {e}, link: {link}")
        
    article_text = ""
    for p in article_paragraphs:
        text = p.get_text(strip=True)
        if text:
            article_text += f"\n{text}"

    

    if len(article_text) < 50:
        print(f"Artikeltext zu kurz, überspringe: {link}.")
        return None

    return [
        article_headline, 
        link, 
        date, 
        article_text.strip(), 
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ]
        
    


def scrape_theconversation():
    articles = []
    articles_link = get_links_from_theconversation_rss()
    articles_link = articles_link
    if articles_link is None:
        print("Keine Artikel gefunden.")
        return []
    else:
        for link in articles_link:
            articles.append(scrape_article(link))
            #time.sleep(2)
    return articles


if __name__ == "__main__":
    print("Starte The Conversation Scraping")
    theconversation_articles = scrape_theconversation()
    print("The Conversation abgeschlossen")
    for article in theconversation_articles:
        if article is not None:
            print(f"Headline: {article[0]}")
            print(f"Link: {article[1]}")
            print(f"Datum: {article[2]}")
            print(f"Artikeltext: {article[3][:200]}...")
            print(f"Scraped am: {article[4]}")
            print("-" * 80)