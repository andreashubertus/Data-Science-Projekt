import streamlit as st
import re

VALID_CATEGORIES = {"POLITICS", "ECONOMY", "TECHNOLOGY", "SPORTS", "CULTURE"}

CATEGORY_LABELS = {
    "POLITICS": "🏛️ Politik",
    "ECONOMY": "💼 Wirtschaft",
    "TECHNOLOGY": "🤖 Technologie",
    "SPORTS": "⚽ Sport",
    "CULTURE": "🎭 Kultur",
}

def save_user(name, email, interessen):
    # TODO: Hasan: Datenbankanbindung hier einfügen
    pass

def email_exists(email):
    # TODO: Hasan: Datenbankabfrage hier einfügen
    return False

def is_valid_email(email):
    pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    return re.match(pattern, email) is not None

def registrierung_page():
    st.title("🤖 AI News Summarizer")
    st.subheader("Registrierung")
    st.divider()

    if st.session_state.get("registriert"):
        st.success("✅ Erfolgreich registriert!")
        if st.button("➕ Weitere Person registrieren"):
            st.session_state["registriert"] = False
            st.rerun()
        st.stop()

    name = st.text_input("👤 Name", placeholder="Max Mustermann")
    email = st.text_input("📧 E-Mail", placeholder="max@beispiel.de")

    st.write("🎯 **Interessen auswählen**")
    ausgewaehlte = []
    cols = st.columns(3)

    for i, kategorie in enumerate(sorted(VALID_CATEGORIES)):
        with cols[i % 3]:
            if st.checkbox(CATEGORY_LABELS[kategorie], key=f"{kategorie}"):
                ausgewaehlte.append(kategorie)

    st.divider()

    if st.button("✅ Registrieren", use_container_width=True):
        if not name.strip():
            st.error("Bitte einen Namen eingeben.")
        elif not is_valid_email(email):
            st.error("Bitte eine gültige E-Mail eingeben.")
        elif email_exists(email):
            st.error("Diese E-Mail ist bereits registriert.")
        elif not ausgewaehlte:
            st.error("Bitte mindestens eine Kategorie auswählen.")
        else:
            save_user(name.strip(), email.strip(), ausgewaehlte)
            st.session_state["registriert"] = True
            st.rerun()

registrierung_page()