import scraper_tagesschau
import scraper_theconversation
import time


def main(verbose = False):
    article_list = []
    print("Starte den Scraping-Prozess für Tagesschau...")
    tagesschau_articles,errormessage = scraper_tagesschau.scrape_tagesschau()
    article_list.extend(tagesschau_articles)
    print(f"Tagesschau: {len(tagesschau_articles)} Artikel erfolgreich gescraped.\n")
    if errormessage != "":
        print(errormessage)
    print("Starte den Scraping-Prozess für The Conversation...")
    theconversation_articles,errormessage = scraper_theconversation.scrape_theconversation()
    article_list.extend(theconversation_articles)
    print(f"The Conversation: {len(theconversation_articles)} Artikel-Links erfolgreich gescraped.\n")
    if errormessage != "":
        print(errormessage)
    if verbose:
        for article in article_list:
            if article is not None:
                print(f"Headline: {article[0]}")
                print(f"Link: {article[1]}")
                print(f"Datum: {article[2]}")
                print(f"Artikeltext: {article[3][:200]}...")
                print(f"Scraped am: {article[4]}")
                print("-" * 80)

if __name__ == "__main__":
    start_time = time.time()
    main(verbose=True)
    end_time = time.time()
    print(end_time-start_time)