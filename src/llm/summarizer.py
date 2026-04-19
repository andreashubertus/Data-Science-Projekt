from dotenv import load_dotenv
import os
from pathlib import Path
from groq import Groq

MODEL = "llama-3.3-70b-versatile"
MAX_TOKENS = 300

VALID_CATEGORIES = {"POLITICS", "ECONOMY", "TECHNOLOGY", "SPORTS", "CULTURE"}

SUMMARIZE_PROMPT = (Path(__file__).parent / "prompts" / "summarize.txt").read_text(encoding="utf-8")
CLASSIFY_PROMPT = (Path(__file__).parent / "prompts" / "classify.txt").read_text(encoding="utf-8")

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
                "content": SUMMARIZE_PROMPT
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

def summarize_by_category(db_module, category, chunk_size=5):
    articles = db_module.get_articles_by_category(category)
    summaries = [a["summary"] for a in articles if a["summary"]]
    
    chunks = [summaries[i:i+chunk_size] for i in range(0, len(summaries), chunk_size)]
    chunk_summaries = [summarize_article("\n\n".join(chunk)) for chunk in chunks]
    
    return summarize_article("\n\n".join(chunk_summaries))
    
if __name__ == "__main__":
    import sys
    sys.path.append(str(Path(__file__).parent.parent))
    import db

    db.init_db()
    count = summarize_unsummarized(db)