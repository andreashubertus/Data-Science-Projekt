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
    links = [link['href'] for link in soup.find_all('link') if 'rel' in link.attrs and link['rel'] == 'alternate']
    
    return links


def scrape_article(link):
    if not link.startswith("http"):
        link = "https://theconversation.com" + link
        
    try:
        article_request = requests.get(link, headers=headers)
        if article_request.status_code != 200:
            print(f"Keine Antwort. Status Code: {article_request.status_code}")
        return link
            
        
    except Exception as e:
        print(f"Fehler beim Scrapen des Artikels: {e}, link: {link}")
        return None


def scrape_theconversation():
    articles = []
    articles_link = get_links_from_theconversation_rss()
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
    print("the conversation abgeschlossen")
    for article in theconversation_articles:
        if article is not None:
            print(f"Gefunden: {article}")