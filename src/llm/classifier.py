from dotenv import load_dotenv
import os
from pathlib import Path
from groq import Groq
 
MODEL = "llama-3.3-70b-versatile"
MAX_TOKENS = 10
FALLBACK_CATEGORY = "UNCATEGORIZED"
 
VALID_CATEGORIES = {"POLITICS", "ECONOMY", "TECHNOLOGY", "SPORTS", "CULTURE"}
 
CLASSIFY_PROMPT = (Path(__file__).parent / "prompts" / "classify.txt").read_text(encoding="utf-8")
 
load_dotenv()
 
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
 
 
def classify_article(article: str) -> str:
    if not article or not article.strip():
        raise ValueError("Article text must not be empty.")
    
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": CLASSIFY_PROMPT},
            {"role": "user", "content": article}
        ],
        max_tokens=MAX_TOKENS
    )
    category = response.choices[0].message.content.strip().upper()
 
    if category not in VALID_CATEGORIES:
        logger.warning(
            "LLM returned unrecognized category %r — falling back to %r.",
            category,
            FALLBACK_CATEGORY,
        )
        return FALLBACK_CATEGORY
 
    return category