from dotenv import load_dotenv
import os
from pathlib import Path
from groq import Groq

SYSTEM_PROMPT = (Path(__file__).parent / "prompts" / "summarize.txt").read_text(encoding="utf-8")
load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def summarize_article(article: str) -> str:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": article
            }
        ],
        max_tokens=300
    )
    return response.choices[0].message.content

def summarize_unsummarized(db_module) -> int:
    articles = db_module.get_unsummarized_articles()

    count = 0

    with db_module.get_connection() as conn:
        for article in articles:
            try:
                summary = summarize_article(article["text"])
                conn.execute(
                    "UPDATE articles SET summary = ? WHERE id = ?",
                    (summary, article["id"])
                )
                print(f"✓ {article['headline'][:60]}...")
                count += 1
            except Exception as e:
                print(f"✗ Fehler bei Artikel {article['id']}: {e}")
        conn.commit()

    return count

            