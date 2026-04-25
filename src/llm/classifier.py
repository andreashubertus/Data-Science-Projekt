"""
Classifies a news article into one of the predefined categories using an LLM.

The LLM is expected to respond with a single uppercase category word.
If the response is not a valid category, the article is assigned a fallback.
"""

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

MODEL = "llama-3.3-70b-versatile"
MAX_TOKENS = 10

VALID_CATEGORIES = {"POLITICS", "ECONOMY", "TECHNOLOGY", "SPORTS", "CULTURE"}

FALLBACK_CATEGORY = "UNCATEGORIZED"

_PROMPTS_DIR = Path(__file__).parent / "prompts"


def _load_prompt(filename: str) -> str:
    """Load a prompt file, raising a clear error if it is missing.

    Args:
        filename: Name of the prompt file inside the ``prompts/`` directory.

    Returns:
        Contents of the prompt file as a string.

    Raises:
        FileNotFoundError: If the prompt file does not exist.
    """
    path = _PROMPTS_DIR / filename
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"Prompt file not found: '{path}'. "
            "Make sure the 'prompts/' directory is present next to this module."
        ) from exc


@lru_cache(maxsize=1)
def _get_classify_prompt() -> str:
    """Return the classification prompt, loaded and cached on first use."""
    return _load_prompt("classify.txt")


def _get_client() -> Groq:
    """Create the Groq client lazily so the module remains importable in tests.

    Returns:
        Authenticated :class:`groq.Groq` client instance.

    Raises:
        RuntimeError: If ``GROQ_API_KEY`` is not set in the environment.
    """
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not set. "
            "Export it as an environment variable or add it to your .env file."
        )
    return Groq(api_key=api_key)


def _extract_category(response) -> str:
    """Extract and normalize the category label from a Groq chat response.

    Args:
        response: Raw response object returned by the Groq API.

    Returns:
        Upper-cased, whitespace-stripped content string.

    Raises:
        RuntimeError: If the response structure is unexpected or content is empty.
    """
    try:
        content = response.choices[0].message.content
    except (AttributeError, IndexError, TypeError) as exc:
        raise RuntimeError("LLM returned an invalid response structure.") from exc

    if content is None:
        raise RuntimeError("LLM returned an empty response.")

    return content.strip().upper()


def classify_article(article: str) -> str:
    """Classify a news article into one of the predefined categories.

    Sends the article to the LLM with a classification prompt and parses
    the response. If the model returns an unrecognized category, a fallback
    value is returned and a warning is printed.

    Args:
        article: Raw text of the news article to classify.

    Returns:
        One of the strings in :data:`VALID_CATEGORIES`, or
        :data:`FALLBACK_CATEGORY` if the model response was invalid.

    Raises:
        ValueError: If ``article`` is empty or blank.
        RuntimeError: If the API key is missing or the LLM response is malformed.
        groq.APIError: On connection or authentication errors.
    """
    if not article or not article.strip():
        raise ValueError("Article text must not be empty.")

    client = _get_client()
    classify_prompt = _get_classify_prompt()

    print(f"Sending article to LLM for classification (length={len(article)}).")

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": classify_prompt},
            {"role": "user", "content": article},
        ],
        max_tokens=MAX_TOKENS,
    )

    category = _extract_category(response)

    if category not in VALID_CATEGORIES:
        print(
            f"LLM returned unrecognized category {category!r}; "
            f"falling back to {FALLBACK_CATEGORY!r}."
        )
        return FALLBACK_CATEGORY

    print(f"Article classified as {category!r}.")
    return category
