# Data Science Projekt

## Mailing Part

My part of the project is the mailing module.

It does these steps:

1. Get the latest unsent summary from the DB.
2. Get active subscribers from the DB.
3. Convert DB rows into Python objects.
4. Build the email subject and content.
5. Send the email to each subscriber.
6. Save one delivery result per subscriber.
7. Mark the summary as sent.

Main files:

- `mailing/newsletter_sender.py` - main mailing workflow
- `mailing/mappers.py` - converts and validates DB data
- `mailing/content_builder.py` - builds email subject and body
- `mailing/mailer_service.py` - simulated sending service
- `mailing/models.py` - dataclasses

Important note:

- `name` and `created_at` may be `None`
- `id`, `email`, `title`, and `content` are required
- if required DB data is missing, the mailing code raises a clear error

## TODO For DB Student

The mailing module expects these DB methods:

### `get_latest_unsent_summary()`

Should return:

```python
{
    "id": int,
    "title": str,
    "content": str,
    "created_at": str | None
}
```

If no summary exists, return `None`.

### `get_active_subscribers()`

Should return:

```python
[
    {
        "id": int,
        "email": str,
        "name": str | None,
        "active": bool
    }
]
```

If there are no subscribers, return `[]`.

### `save_delivery_result(summary_id, subscriber_id, success, error_message)`

Should save one sending result.

### `mark_summary_as_sent(summary_id)`

Should mark the summary as sent, so it is not sent again.
## LLM - Zusammenfassung

Der LLM-Teil nutzt die Groq API mit dem Modell `llama-3.3-70b-versatile` 
um gescrapte Artikel automatisch zusammenzufassen.

### Setup

1. Kostenlosen Groq API Key erstellen auf [console.groq.com](https://console.groq.com)

2. Dependencies installieren:
```bash
   pip install groq python-dotenv
```

3. `.env` Datei erstellen (wichtig: ohne BOM-Encoding!):
```powershell
   # Windows
   [System.IO.File]::WriteAllText(".env", "GROQ_API_KEY=dein_key_hier", (New-Object System.Text.UTF8Encoding $false))
   
   # Mac/Linux
   echo "GROQ_API_KEY=dein_key_hier" > .env
```

### Hinweise
- Die `.env` Datei niemals committen
- Den API Key auf [console.groq.com](https://console.groq.com) generieren und einfügen
- Groq ist kostenlos mit 14.400 Anfragen pro Tag
