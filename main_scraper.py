import scraper_tagesschau
import scraper_theconversation


def main():
    print("Starte den Scraping-Prozess für Tagesschau...")
    tagesschau_articles = scraper_tagesschau.scrape_tagesschau()
    print(f"Tagesschau: {len(tagesschau_articles)} Artikel erfolgreich gescraped.\n")
    
    print("Starte den Scraping-Prozess für The Conversation...")
    theconversation_articles = scraper_theconversation.get_links_from_theconversation_rss()
    print(f"The Conversation: {len(theconversation_articles)} Artikel-Links erfolgreich gescraped.\n")


if __name__ == "__main__":
    main()