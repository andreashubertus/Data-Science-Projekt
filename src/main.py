import logging

try:
    from src.database import database
except ModuleNotFoundError:
    from database import database


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:%(name)s:%(message)s",
)

logger = logging.getLogger(__name__)


def run_pipeline() -> None:
    """Run the project pipeline skeleton.

    Current status:
    - database initialization is ready
    - scraper integration is still pending
    - LLM/database integration still needs final alignment
    - mailing integration still depends on the category-aware DB layer
    """
    logger.info("Starting project pipeline.")

    database.init_db()
    logger.info("Database initialized.")

    # TODO: Enable the scraper step once the scraper module is finalized.
    #
    # Example future integration:
    # from src.scraping.main_scraper import scrape_all_sources
    # articles = scrape_all_sources()
    # inserted_count = database.insert_articles(articles)
    # logger.info("Inserted %s new article(s).", inserted_count)

    # TODO: Connect article classification once the DB layer stores categories.
    #
    # Example future integration:
    # unsorted_articles = database.get_unsummarized_articles()
    # for article in unsorted_articles:
    #     category = classify_article(article["text"])
    #     database.save_article_category(article["id"], category)

    # TODO: Build one digest per category once DB helper functions are aligned.
    #
    # Example future integration:
    # for category in VALID_CATEGORIES:
    #     build_category_digest(database, category)

    # TODO: Enable mailing once the DB layer provides the category-aware
    # mailing contract expected by src.mailing.newsletter_sender:
    # - get_latest_unsent_summary() returning a summary with "category"
    # - get_active_subscribers(category)
    # - save_delivery_result(...)
    # - mark_summary_as_sent(...)
    #
    # Example future integration:
    # send_latest_newsletter(database)

    logger.info("Pipeline skeleton finished. Remaining steps are marked as TODO.")


if __name__ == "__main__":
    run_pipeline()
