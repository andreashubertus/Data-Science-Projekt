# Data Science Projekt

This project builds an AI news pipeline:

1. collect news articles
2. classify and summarize them with an LLM
3. store summaries in the database
4. send category-based email newsletters to subscribers

## Project Structure

Source code:

- `src/database/` - database logic
- `src/llm/` - article classification and summarization
- `src/mailing/` - newsletter generation and SMTP sending
- `src/main.py` - future main pipeline entry point

Tests:

- `tests/llm/` - tests for classifier and summarizer
- `tests/mailing/` - tests for mailing logic
- `tests/database/` - database-related tests

Scripts:

- `scripts/mailing_demo.py` - local demo script for the mailing flow

## Mailing Module

The mailing module:

1. loads the latest unsent summary from the database
2. reads the summary category
3. loads active subscribers for that category
4. builds text and HTML email content
5. sends emails over SMTP
6. stores delivery results
7. marks the summary as sent

Important mailing logic:

- summaries and subscribers now include a `category`
- newsletters are sent only to subscribers of the matching category
- SMTP configuration is loaded from `.env`

Main mailing files:

- `src/mailing/newsletter_sender.py`
- `src/mailing/content_builder.py`
- `src/mailing/mailer_service.py`
- `src/mailing/mappers.py`
- `src/mailing/models.py`
- `src/mailing/config_mailing.py`

## Setup

Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Create a local `.env` file based on `.env.example`.

Required environment variables:

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
- for Gmail SMTP, use an App Password instead of your normal password

## Tests

Run all mailing tests:

```bash
python3 -m pytest tests/mailing -q
```

Run all LLM tests:

```bash
python3 -m pytest tests/llm -q
```

Run the mailing demo:

```bash
python3 scripts/mailing_demo.py
```
