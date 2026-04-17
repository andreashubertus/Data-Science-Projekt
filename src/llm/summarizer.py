from dotenv import load_dotenv
import os
from pathlib import Path
from groq import Groq

SYSTEM_PROMPT = (Path(__file__).parent / "prompts" / "summarize.txt").read_text(encoding="utf-8")
MODEL = "llama-3.3-70b-versatile"
MAX_TOKENS = 300

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def summarize_article(article: str) -> str:
    """Summarizes a news article using the Groq API.

    Args:
        article (str): The full text of the news article.

    Returns:
        str: A summary of the article.

    Raises:
        groq.GroqError: If the API is unreachable or the key is invalid.
    """
    response = client.chat.completions.create(
        model=MODEL,
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
        max_tokens=MAX_TOKENS
    )
    return response.choices[0].message.content

def summarize_unsummarized(db_module) -> int:
    articles = db_module.get_unsummarized_articles()

    if not articles:
        print("Keine neuen Artikel zum Zusammenfassen.")
        return 0
    
    count = 0

    for article in articles:
        try:
            summary = summarize_article(article["text"])
            db_module.update_summary(article["id"], summary)
            count += 1
        except Exception as e:
            print(f"Fehler bei Artikel {article['id']}: {e}")

    return count
    
if __name__ == "__main__":
    import sys
    sys.path.append(str(Path(__file__).parent.parent))
    import db

    db.init_db()
    count = summarize_unsummarized(db)