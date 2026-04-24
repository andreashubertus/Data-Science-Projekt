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

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

MODEL = "llama-3.3-70b-versatile"
MAX_TOKENS_CHUNK = 300
MAX_TOKENS_DIGEST = 500

VALID_CATEGORIES = {"POLITICS", "ECONOMY", "TECHNOLOGY", "SPORTS", "CULTURE"}

_PROMPTS_DIR = Path(__file__).parent / "prompts"

load_dotenv()


def _get_client() -> Groq:
    """Create the Groq client lazily so the module remains importable in tests."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set.")
    return Groq(api_key=api_key)


def _load_prompt(filename: str) -> str:
    """Load a prompt file, raising a clear error if it is missing."""
    path = _PROMPTS_DIR / filename
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"Prompt file not found: '{path}'. "
            "Make sure the 'prompts/' directory is present next to this module."
        ) from exc


@lru_cache(maxsize=1)
def _get_chunk_prompt() -> str:
    """Return the chunk summarization prompt, loaded on first use."""
    return _load_prompt("summarize_chunk.txt")


@lru_cache(maxsize=1)
def _get_digest_prompt() -> str:
    """Return the digest summarization prompt, loaded on first use."""
    return _load_prompt("summarize_digest.txt")


def _extract_completion_text(response) -> str:
    """Extract the first completion text from a Groq response."""
    try:
        content = response.choices[0].message.content
    except (AttributeError, IndexError, TypeError) as exc:
        raise RuntimeError("LLM returned an invalid response structure.") from exc

    if content is None:
        raise RuntimeError("LLM returned an empty response.")

    return content.strip()


def _generate_completion(system_prompt: str, user_content: str, max_tokens: int) -> str:
    """Generate a completion from the LLM for a system and user prompt pair.

    Args:
        system_prompt: Instruction text that defines the model's task.
        user_content: Input text passed to the model as the user message.
        max_tokens: Maximum number of tokens the model may generate.

    Returns:
        Trimmed text content from the first model response choice.

    Raises:
        RuntimeError: If the API key is missing or the LLM response is malformed.
        groq.APIError: On connection, authentication, or API request errors.
    """
    client = _get_client()
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        max_tokens=max_tokens,
    )
    return _extract_completion_text(response)


def summarize_chunk(articles: list[str]) -> str:
    """Summarizes a list of article texts into a short intermediate summary.

    The articles are joined with a separator and sent together to the LLM.
    The result is used as input for :func:`summarize_digest`.

    Args:
        articles: List of raw article text strings.

    Returns:
        Summary of the chunk as a single string. Returns an empty string if
        ``articles`` is empty.

    Raises:
        RuntimeError: If the API key is missing or the LLM response is malformed.
        groq.APIError: On connection or authentication errors.
    """
    if not articles:
        return ""

    combined = "\n\n---\n\n".join(articles)
    return _generate_completion(_get_chunk_prompt(), combined, MAX_TOKENS_CHUNK)


def summarize_digest(chunk_summaries: list[str]) -> str:
    """Condenses multiple chunk summaries into a single overall digest.

    Args:
        chunk_summaries: List of individual summaries produced by
            :func:`summarize_chunk`.

    Returns:
        Final digest text as a single string. Returns an empty string if
        ``chunk_summaries`` is empty.

    Raises:
        RuntimeError: If the API key is missing or the LLM response is malformed.
        groq.APIError: On connection or authentication errors.
    """
    if not chunk_summaries:
        return ""

    combined = "\n\n".join(chunk_summaries)
    return _generate_completion(_get_digest_prompt(), combined, MAX_TOKENS_DIGEST)


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
