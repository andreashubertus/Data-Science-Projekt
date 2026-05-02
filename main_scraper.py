import scraper_tagesschau
import scraper_theconversation


def main():
    article_list = []
    print("Starte den Scraping-Prozess für Tagesschau...")
    tagesschau_articles,errormessage = scraper_tagesschau.scrape_tagesschau()
    article_list.append(tagesschau_articles)
    print(f"Tagesschau: {len(tagesschau_articles)} Artikel erfolgreich gescraped.\n")
    
    print("Starte den Scraping-Prozess für The Conversation...")
    theconversation_articles,errormassage = scraper_theconversation.get_links_from_theconversation_rss()
    article_list.append(theconversation_articles)
    print(f"The Conversation: {len(theconversation_articles)} Artikel-Links erfolgreich gescraped.\n")
    
    for article in article_list:
        if article is not None:
            print(f"Headline: {article[0]}")
            print(f"Link: {article[1]}")
            print(f"Datum: {article[2]}")
            print(f"Artikeltext: {article[3][:200]}...")
            print(f"Scraped am: {article[4]}")
            print("-" * 80)

if __name__ == "__main__":
    main()