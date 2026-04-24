"""
Classifies a news article into one of the predefined categories using an LLM.
 
The LLM is expected to respond with a single uppercase category word.
If the response is not a valid category, the article is assigned a fallback.
"""

from dotenv import load_dotenv
import os
from pathlib import Path
from groq import Groq
import logging
 
logger = logging.getLogger(__name__)
 
MODEL = "llama-3.3-70b-versatile"
MAX_TOKENS = 10
 
VALID_CATEGORIES = {"POLITICS", "ECONOMY", "TECHNOLOGY", "SPORTS", "CULTURE"}
FALLBACK_CATEGORY = "UNCATEGORIZED"
 
CLASSIFY_PROMPT = (Path(__file__).parent / "prompts" / "classify.txt").read_text(encoding="utf-8")
 
load_dotenv()

api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise RuntimeError("GROQ_API_KEY is not set.")

client = Groq(api_key=api_key)


def classify_article(article: str) -> str:
    """Classifies a news article into one of the predefined categories.
 
    Sends the article to the LLM with a classification prompt and parses
    the response. If the model returns an unrecognized category, a fallback
    value is returned and a warning is logged.
 
    Args:
        article: Raw text of the news article to classify.
 
    Returns:
        One of the strings in :data:`VALID_CATEGORIES`, or
        :data:`FALLBACK_CATEGORY` if the model response was invalid.
 
    Raises:
        ValueError: If ``article`` is empty or blank.
        groq.APIError: On connection or authentication errors.
    """
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