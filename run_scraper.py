from scraper_tagesschau import scrape_tagesschau
from src.database.database import init_db, insert_articles


if __name__ == "__main__":
    init_db()
    print("Scraping articles...")
    articles = scrape_tagesschau()
    count = insert_articles(articles)
    print(f"{count} neue Artikel in die Datenbank eingefügt.")
