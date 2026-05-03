from scraper_tagesschau import scrape_tagesschau
from src.database.connection import init_db
from src.database.articles import insert_articles, transfer_article_categories
from src.llm.summarizer import build_category_digest


if __name__ == "__main__":
    init_db()
    print("Scraping articles...")
    articles = scrape_tagesschau()
    count = insert_articles(articles)
    print(f"{count} neue Artikel in die Datenbank eingefügt.")
    transfer_article_categories()
    build_category_digest("POLITICS")
