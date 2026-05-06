# AI News Summarizer

This project collects online news articles, classifies them into categories, creates AI-generated digests, stores the results in a local SQLite database, and sends category-based email newsletters to subscribers.

## Features

- scrape articles from Tagesschau and The Conversation
- classify articles into `POLITICS`, `ECONOMY`, `TECHNOLOGY`, `SPORTS`, and `CULTURE`
- build category digests with Groq
- store articles, digests, subscribers, and delivery results in SQLite
- send newsletters via SMTP
- register subscribers with category preferences in a Streamlit panel

## Project Structure

- `src/database/` - SQLite database logic
- `src/scraper/` - news scrapers
- `src/llm/` - classification and summarization
- `src/mailing/` - newsletter generation and sending
- `src/register_new_user/` - Streamlit registration panel
- `src/main.py` - full project pipeline
- `scripts/` - helper scripts for local setup and demos
- `tests/` - unit and integration tests

## Setup

Recommended environment:

- Python 3.14 was used during development and testing
- install dependencies from `requirements.txt`

Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Create a `.env` file based on `.env.example`.

How to get a Groq API key:

1. create a Groq account at [console.groq.com](https://console.groq.com/)
2. open the API Keys section in the Groq console
3. create a new API key
4. copy the key into your local `.env` file as `GROQ_API_KEY`

Required values:

```env
GROQ_API_KEY=your_key_here
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@example.com
SMTP_PASSWORD=your_app_password
SMTP_SENDER_EMAIL=your_email@example.com
SMTP_USE_TLS=true
```

Notes:

- do not commit `.env`
- for Gmail SMTP, use an app password
- Groq rate limits can slow down large runs

## How To Run

Initialize a fresh local database:

```bash
python3 scripts/reset_database.py
```

Add example subscribers:

```bash
python3 scripts/seed_subscribers.py
```

Run the full pipeline:

```bash
python3 main.py
```

Open the registration panel:

```bash
streamlit run src/register_new_user/Subscribe_panel.py
```

Run the mailing demo:

```bash
python3 scripts/mailing_demo.py
```

## Tests

Run the full test suite:

```bash
python3 -m pytest -q
```

Useful subsets:

```bash
python3 -m pytest tests/database -q
python3 -m pytest tests/mailing -q
python3 -m pytest tests/scraping -q
python3 -m pytest tests/llm/test_classifier.py -q
python3 -m pytest tests/llm/test_summarizer.py -q
```

## Current Status

The project is ready for demonstration:

- database, scraping, mailing, and classification are integrated
- newsletter sending works with category-based subscribers
- helper scripts are included for reset and test data setup
- most testing is automated; live API behavior still depends on Groq limits and website availability
