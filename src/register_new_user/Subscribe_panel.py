from pathlib import Path
import re
import sqlite3
import sys

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.database.connection import init_db
from src.database.subscriber import add_subscriber


VALID_CATEGORIES = {"POLITICS", "ECONOMY", "TECHNOLOGY", "SPORTS", "CULTURE"}

CATEGORY_LABELS = {
    "POLITICS": "🏛️ Politik",
    "ECONOMY": "💼 Wirtschaft",
    "TECHNOLOGY": "🤖 Technologie",
    "SPORTS": "⚽ Sport",
    "CULTURE": "🎭 Kultur",
}


def email_exists(email: str) -> bool:
    """Return True when the email is already registered."""
    from src.database.connection import get_connection

    with get_connection() as conn:
        row = conn.execute(
            "SELECT 1 FROM subscribers WHERE email = ? LIMIT 1",
            (email,),
        ).fetchone()
    return row is not None


def save_user(name: str, email: str, interests: list[str]) -> bool:
    """Persist one user with the selected newsletter categories."""
    categories = sorted(set(interests))
    return add_subscriber(email=email, name=name, categories=categories)


def is_valid_email(email: str) -> bool:
    """Check whether the input looks like a valid email address."""
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email) is not None


def registrierung_page() -> None:
    """Render the Streamlit registration page."""
    init_db()

    st.set_page_config(page_title="AI News Summarizer Registrierung")
    st.title("AI News Summarizer")
    st.subheader("Registrierung für den Newsletter")
    st.divider()

    if st.session_state.get("registriert"):
        st.success("Erfolgreich registriert!")
        if st.button("Weitere Person registrieren"):
            st.session_state["registriert"] = False
            st.rerun()
        st.stop()

    name = st.text_input("Name", placeholder="Max Mustermann")
    email = st.text_input("E-Mail", placeholder="max@beispiel.de")

    st.write("Interessen auswählen")
    selected_categories = []
    cols = st.columns(3)

    for i, category in enumerate(sorted(VALID_CATEGORIES)):
        with cols[i % 3]:
            if st.checkbox(CATEGORY_LABELS[category], key=f"category_{category}"):
                selected_categories.append(category)

    st.divider()

    if st.button("Registrieren", use_container_width=True):
        normalized_name = name.strip()
        normalized_email = email.strip().lower()

        if not normalized_name:
            st.error("Bitte einen Namen eingeben.")
            return

        if not is_valid_email(normalized_email):
            st.error("Bitte eine gültige E-Mail eingeben.")
            return

        if not selected_categories:
            st.error("Bitte mindestens eine Kategorie auswählen.")
            return

        if email_exists(normalized_email):
            st.error("Diese E-Mail ist bereits registriert.")
            return

        try:
            created = save_user(
                normalized_name,
                normalized_email,
                selected_categories,
            )
        except sqlite3.Error as exc:
            st.error(f"Fehler beim Speichern in der Datenbank: {exc}")
            return

        if not created:
            st.error("Registrierung konnte nicht gespeichert werden.")
            return

        st.session_state["registriert"] = True
        st.rerun()


registrierung_page()
