from dotenv import load_dotenv
import os
from pathlib import Path
from groq import Groq

MODEL = "llama-3.3-70b-versatile"
MAX_TOKENS_CHUNK = 300
MAX_TOKENS_DIGEST = 500

VALID_CATEGORIES = {"POLITICS", "ECONOMY", "TECHNOLOGY", "SPORTS", "CULTURE"}

CHUNK_PROMPT = (Path(__file__).parent / "prompts" / "summarize_chunk.txt").read_text(encoding="utf-8")
DIGEST_PROMPT = (Path(__file__).parent / "prompts" / "summarize_digest.txt").read_text(encoding="utf-8")

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def _summarize_chunk(articles: list[str]) -> str:
    combined = "\n\n---\n\n".join(articles)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": CHUNK_PROMPT},
            {"role": "user", "content": combined}
        ],
        max_tokens=MAX_TOKENS_CHUNK
    )
    return response.choices[0].message.content

def _summarize_digest(chunk_summaries: list[str])-> str:
    combined = "\n\n".join(chunk_summaries)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": DIGEST_PROMPT},
            {"role": "user", "content": combined}
        ],
        max_tokens=MAX_TOKENS_DIGEST
    )
    return response.choices[0].message.content

def build_category_digest(db_module, category: str, chunk_size: int = 5) -> str:
    if category not in VALID_CATEGORIES:
        raise ValueError(f"Invalid category '{category}'. Must be one of {VALID_CATEGORIES}")
 
    articles = db_module.get_articles_by_category(category)
    texts = [a["text"] for a in articles if a["text"]]
 
    if not texts:
        return f"No articles available for category {category}."
 
    chunks = [texts[i:i + chunk_size] for i in range(0, len(texts), chunk_size)]
 
    chunk_summaries = []
    for i, chunk in enumerate(chunks):
        chunk_summaries.append(_summarize_chunk(chunk))
 
    digest = _summarize_digest(chunk_summaries)
 
    db_module.save_digest(category, digest)
 
    return digest


if __name__ == "__main__":
    import sys
    sys.path.append(str(Path(__file__).parent.parent))
    import db

    db.init_db()
    count = summarize_unsummarized(db)