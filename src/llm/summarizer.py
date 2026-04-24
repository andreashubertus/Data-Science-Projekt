"""
Summarizes news articles by category and builds personalized newsletters
for subscribers.
 
Pipeline:
  1. Articles for a given category are loaded from the database.
  2. They are split into chunks and each chunk is summarized individually
     (``summarize_chunk``).
  3. The chunk summaries are condensed into a single overall digest
     (``summarize_digest``).
  4. The digest is persisted to the database and returned.
"""
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

api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise RuntimeError("GROQ_API_KEY is not set.")

client = Groq(api_key=api_key)

def _generate_completion(system_prompt: str, user_content: str, max_tokens: int) -> str:
    """Send a prompt pair to the LLM and return the trimmed text response."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content.strip()


def summarize_chunk(articles: list[str]) -> str:
    """Summarizes a list of article texts into a short intermediate summary.
 
    The articles are joined with a separator and sent together to the LLM.
    The result is used as input for :func:`summarize_digest`.
 
    Args:
        articles: List of raw article text strings.
 
    Returns:
        Summary of the chunk as a single string.
 
    Raises:
        groq.APIError: On connection or authentication errors.
    """
    if not articles:
        return ""
    
    combined = "\n\n---\n\n".join(articles)
    return _generate_completion(CHUNK_PROMPT, combined, MAX_TOKENS_CHUNK)


def summarize_digest(chunk_summaries: list[str]) -> str:
    """Condenses multiple chunk summaries into a single overall digest.
 
    Args:
        chunk_summaries: List of individual summaries produced by
            :func:`summarize_chunk`.
 
    Returns:
        Final digest text as a single string.
 
    Raises:
        groq.APIError: On connection or authentication errors.
    """
    if not chunk_summaries:
        return ""

    combined = "\n\n".join(chunk_summaries)
    return _generate_completion(DIGEST_PROMPT, combined, MAX_TOKENS_DIGEST)

def build_category_digest(db_module, category: str, chunk_size: int = 5) -> str:
    """Builds and persists the digest for a news category.
 
    Loads all articles for the category from the database, splits them into
    chunks, summarizes each chunk, and produces a final digest that is then
    saved to the database.
 
    Args:
        db_module: Database module exposing ``get_articles_by_category``,
            ``save_digest`` (and ``get_latest_digest`` for the newsletter).
        category: Upper-case category name, e.g. ``"TECHNOLOGY"``.
            Must be a member of :data:`VALID_CATEGORIES`.
        chunk_size: Number of articles per chunk (default: 5).
 
    Returns:
        Final digest text, or an info message when no articles are available.
 
    Raises:
        ValueError: When ``category`` is not in :data:`VALID_CATEGORIES`.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0.")
    category = category.upper()

    if category not in VALID_CATEGORIES:
        raise ValueError(f"Invalid category '{category}'. Must be one of {VALID_CATEGORIES}")
 
    articles = db_module.get_articles_by_category(category)
    texts = [a.get("text") for a in articles if a.get("text")]
 
    if not texts:
        return f"No articles available for category {category}."
 
    chunks = [texts[i:i + chunk_size] for i in range(0, len(texts), chunk_size)]
 
    chunk_summaries = []
    for chunk in chunks:
        chunk_summaries.append(summarize_chunk(chunk))
 
    digest = summarize_digest(chunk_summaries)
 
    db_module.save_digest(category, digest)
 
    return digest

def build_all_digests(db_module, chunk_size: int = 5) -> dict[str, str]:
    """Builds digests for all valid categories.
 
    Args:
        db_module: Database module (see :func:`build_category_digest`).
        chunk_size: Articles per chunk (default: 5).
 
    Returns:
        Dictionary mapping category names to their digest texts.
    """
    digests = {}
    for category in sorted(VALID_CATEGORIES):
        digests[category] = build_category_digest(db_module, category, chunk_size)
    return digests

def build_newsletter_for_subscriber(db_module, email: str) -> str:
    """Builds a personalized newsletter for a subscriber.
 
    Reads the subscriber's categories from the database and assembles the
    most recent digests into a formatted Markdown text.
 
    Args:
        db_module: Database module exposing ``get_subscriber_categories``
            and ``get_latest_digest``.
        email: The subscriber's email address.
 
    Returns:
        Formatted newsletter text, or an info message when no subscriptions
        or digests are available.
    """
    categories = db_module.get_subscriber_categories(email)
 
    if not categories:
        return "No category subscriptions found for this subscriber."
 
    sections = []
    for category in categories:
        category = category.upper()
        digest = db_module.get_latest_digest(category)
        if digest:
            sections.append(f"## {category.capitalize()}\n\n{digest}")
 
    if not sections:
        return "No digests available yet for your subscribed categories."
 
    return "\n\n---\n\n".join(sections)
