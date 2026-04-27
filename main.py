"""
Project pipeline:

1. Scraper collects news articles
2. Articles are stored in the database (raw data)
3. Summarizer generates AI summaries from stored articles
4. Summaries are stored in the database (derived data)
5. Mailing module sends summaries to subscribers

main.py will orchestrate this workflow.
"""