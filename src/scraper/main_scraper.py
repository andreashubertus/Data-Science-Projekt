import time

try:
    from src.scraper import scraper_tagesschau, scraper_theconversation
except ModuleNotFoundError:
    import scraper_tagesschau
    import scraper_theconversation


def scrape_all_sources(verbose=False):
    """Scrape all configured news sources and return collected articles.

    Args:
        verbose: When True, prints a short preview for each scraped article.

    Returns:
        Tuple ``(articles, errors)`` where ``articles`` is a flat list of
        scraped article tuples and ``errors`` is a list of non-empty error
        messages from the individual scrapers.
    """
    article_list = []
    errors = []

    tagesschau_articles, errormessage = scraper_tagesschau.scrape_tagesschau()
    article_list.extend(tagesschau_articles)
    if errormessage:
        errors.append(f"Tagesschau: {errormessage}")

    theconversation_articles, errormessage = scraper_theconversation.scrape_theconversation()
    article_list.extend(theconversation_articles)
    if errormessage:
        errors.append(f"The Conversation: {errormessage}")

    if verbose:
        for article in article_list:
            if article is not None:
                print(f"Headline: {article[0]}")
                print(f"Link: {article[1]}")
                print(f"Datum: {article[2]}")
                print(f"Artikeltext: {article[3][:200]}...")
                print(f"Scraped am: {article[4]}")
                print("-" * 80)
    return article_list, errors


def main(verbose=False):
    """Run all scrapers and print a small command-line summary."""
    print("Starte den Scraping-Prozess für Tagesschau und The Conversation...")
    article_list, errors = scrape_all_sources(verbose=verbose)
    print(f"Insgesamt {len(article_list)} Artikel erfolgreich gescraped.\n")
    for error in errors:
        print(error)
    return article_list, errors

if __name__ == "__main__":
    start_time = time.time()
    main(verbose=True)
    end_time = time.time()
    print(end_time-start_time)
