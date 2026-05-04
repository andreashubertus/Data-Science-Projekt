from unittest.mock import patch


def test_run_pipeline_executes_all_steps():
    scraped_articles = [
        ("Headline", "https://example.com/article", "2026-05-04", "Article text", "2026-05-04 10:00:00")
    ]

    with (
        patch("src.main.database.init_db") as mock_init_db,
        patch("src.main.scrape_all_sources", return_value=(scraped_articles, ["scraper warning"])) as mock_scrape,
        patch("src.main.database.insert_articles", return_value=1) as mock_insert_articles,
        patch("src.main.database.transfer_article_categories", return_value=(1, 0)) as mock_transfer_categories,
        patch("src.main.build_category_digest", side_effect=["digest-a", "No articles available for category SPORTS."]) as mock_build_digest,
        patch("src.main.send_latest_newsletter", side_effect=[[object(), object()], []]) as mock_send_newsletter,
        patch("src.main.VALID_CATEGORIES", ["TECHNOLOGY", "SPORTS"]),
    ):
        from src.main import run_pipeline

        run_pipeline()

    mock_init_db.assert_called_once_with()
    mock_scrape.assert_called_once_with()
    mock_insert_articles.assert_called_once_with(scraped_articles)
    mock_transfer_categories.assert_called_once()
    assert mock_transfer_categories.call_args.args[0] is not None
    assert mock_build_digest.call_args_list[0].args == ("SPORTS",)
    assert mock_build_digest.call_args_list[1].args == ("TECHNOLOGY",)
    assert mock_send_newsletter.call_args_list[0].args[1] == "SPORTS"
    assert mock_send_newsletter.call_args_list[1].args[1] == "TECHNOLOGY"
