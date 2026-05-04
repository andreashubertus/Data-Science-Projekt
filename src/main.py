import logging

try:
    from src.database import database
    from src.llm.classifier import classify_article
    from src.llm.summarizer import VALID_CATEGORIES, build_category_digest
    from src.mailing.newsletter_sender import send_latest_newsletter
    from src.scraper.main_scraper import scrape_all_sources
except ModuleNotFoundError:
    from database import database
    from llm.classifier import classify_article
    from llm.summarizer import VALID_CATEGORIES, build_category_digest
    from mailing.newsletter_sender import send_latest_newsletter
    from scraper.main_scraper import scrape_all_sources


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:%(name)s:%(message)s",
)

logger = logging.getLogger(__name__)


def run_pipeline() -> None:
    """Run the full project pipeline from scraping to mailing."""
    logger.info("Starting project pipeline.")

    database.init_db()
    logger.info("Database initialized.")

    scraped_articles, scrape_errors = scrape_all_sources()
    logger.info("Scraper collected %s article(s).", len(scraped_articles))
    for error in scrape_errors:
        logger.warning(error)

    inserted_count = database.insert_articles(scraped_articles)
    logger.info("Inserted %s new article(s) into the database.", inserted_count)

    updated_count, skipped_count = database.transfer_article_categories(classify_article)
    logger.info(
        "Classification finished: %s article(s) updated, %s skipped.",
        updated_count,
        skipped_count,
    )

    built_digests = 0
    sent_deliveries = 0

    for category in sorted(VALID_CATEGORIES):
        try:
            digest = build_category_digest(category)
            if digest.startswith("No articles available"):
                logger.info(
                    "No digest built for category=%s because no articles are available.",
                    category,
                )
            else:
                built_digests += 1
                logger.info("Built digest for category=%s.", category)
        except Exception:
            logger.exception("Failed to build digest for category=%s.", category)

        try:
            results = send_latest_newsletter(database, category)
            sent_deliveries += len(results)
            logger.info(
                "Newsletter delivery for category=%s finished with %s result(s).",
                category,
                len(results),
            )
        except Exception:
            logger.exception("Failed to send newsletter for category=%s.", category)

    logger.info(
        "Pipeline finished. Built %s digest(s) and processed %s delivery result(s).",
        built_digests,
        sent_deliveries,
    )


if __name__ == "__main__":
    run_pipeline()
