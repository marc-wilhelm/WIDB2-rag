import streamlit as st
import sys
from pathlib import Path

# Füge src/ zum Python-Pfad hinzu
# Von streamlit/pages/ aus: ../../src/
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent  # Zwei Ebenen hoch = Root
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from MarkdownCleaner import MultiMarkdownCleaner
from VectoreStoreManager import VectorStoreManager
from RagAgent import RAGAgent
import config
import os
from dotenv import load_dotenv

# Lade Umgebungsvariablen (aus Root-Verzeichnis)
load_dotenv(project_root / ".env")

# Seitenkonfiguration
st.set_page_config(
    page_title="WIDB2 - RAG Chatbot",
    page_icon="🤖"
)

st.title("RAG-Chatbot für BWA")
st.markdown("Stelle Fragen zu den Controlling-Berichten und erhalte präzise Antworten basierend auf den Dokumenten.")

st.markdown("---")

# Beispiel-Fragen
st.markdown("### 💡 Beispiel-Fragen")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **Allgemeine Fragen:**
    - Welche Monate werden in den Berichten von Home Tech behandelt?
    - Gib mir eine Übersicht über die Berichte
    """)

with col2:
    st.markdown("""
    **Spezifische Analysen:**
    - Wie waren die Umsatzerlöse im Januar 2023 von Digital Solutions?
    - In welchem Monat war das Betriebsergebnis von Home Tech am höchsten?
    """)

with col3:
    st.markdown("""
    **Vergleiche:**
    - Wie entwickelten sich die Kosten von Home Tech im Vergleich zu Digital Solutions über die Monate?
    - Welche Faktoren beeinflussten das Ergebnis von Home Tech und Digital Solutions?
    """)

st.markdown("---")


# Initialisierung des RAG-Systems
@st.cache_resource
def initialize_rag_system():
    """
    Lädt das bestehende RAG-System.
    Erstellt KEINE neue Datenbank - dafür init.py verwenden!
    """
    try:
        # API-Key laden
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            st.error("❌ ANTHROPIC_API_KEY nicht in .env gefunden!")
            st.stop()

        # Pfade
        db_path = config.CHROMA_DB_PATH

        # Prüfe ob DB existiert
        if not db_path.exists():
            st.error("❌ Keine Datenbank gefunden!")
            st.info("💡 Bitte führe zuerst `python src/init.py` aus, um die Datenbank zu erstellen.")
            st.stop()

        with st.spinner("🔄 Lade RAG-System..."):
            # Bestehende DB laden
            vector_store = VectorStoreManager(
                db_path=config.CHROMA_DB_PATH,
                collection_name="controlling_berichte"
            )

            # Anzahl der Chunks ermitteln
            collection = vector_store.collection
            num_chunks = collection.count()

            # RAG-Agent initialisieren
            rag_agent = RAGAgent(
                vector_store=vector_store,
                api_key=api_key
            )

            return rag_agent, num_chunks

    except Exception as e:
        st.error(f"❌ Fehler beim Laden: {e}")
        st.exception(e)
        st.stop()

# Sidebar-Kontrollen für DB-Verwaltung
with st.sidebar:
    st.markdown("### 🗄️ Datenbank-Verwaltung")

    # Prüfe ob DB existiert
    db_exists = config.CHROMA_DB_PATH.exists()
    if db_exists:
        st.success("✅ Datenbank vorhanden")

        # Button zum Löschen der DB
        st.markdown("---")
        st.markdown("#### 🗑️ Datenbank zurücksetzen")
        st.warning("⚠️ Dies löscht die gesamte Vektordatenbank!")

        if st.button("🗑️ DB löschen und App stoppen", type="secondary"):
            import shutil

            try:
                # Versuche DB zu löschen
                shutil.rmtree(config.CHROMA_DB_PATH)
                st.success("✅ Datenbank gelöscht!")
                st.info("ℹ️ **Nächste Schritte:**")
                st.code("python src/init_db.py", language="bash")
                st.info("Danach starte die App neu.")
                st.stop()
            except Exception as e:
                st.error(f"❌ Fehler beim Löschen: {e}")
                st.error("💡 **Manuelle Lösung:**")
                st.markdown("1. Stoppe die App (Strg+C im Terminal)")
                st.markdown(f"2. Lösche manuell: `{config.CHROMA_DB_PATH}`")
                st.markdown("3. Führe aus: `python src/init_db.py`")
                st.markdown("4. Starte App neu: `streamlit run streamlit/Home.py`")
                st.stop()
    else:
        st.error("❌ Keine Datenbank gefunden")
        st.info("💡 **Datenbank erstellen:**")
        st.code("python src/init_db.py", language="bash")
        st.stop()

    st.markdown("---")

# RAG-System laden
rag_agent, num_chunks = initialize_rag_system()

# Erfolgreiche Initialisierung anzeigen
with st.sidebar:
    st.success("✅ RAG-System bereit")
    st.info(f"📄 {num_chunks} Chunks geladen")
    st.markdown("---")
    st.markdown("### ℹ️ Hinweise")
    st.markdown("""
    - Stelle Fragen zu den Monatsberichten
    - Das System antwortet nur basierend auf den verfügbaren Dokumenten
    - Bei Unsicherheit wird das klar kommuniziert
    """)

    # Button zum Löschen des Chats
    if st.button("🗑️ Chat löschen"):
        st.session_state.messages = []
        st.rerun()

# Chat-Verlauf initialisieren
if 'messages' not in st.session_state:
    st.session_state.messages = []
    # Begrüßungsnachricht
    st.session_state.messages.append({
        'role': 'assistant',
        'content': 'Hallo! Ich bin dein RAG-Assistent für BWA-Analysen. Stelle mir Fragen zu den Controlling-Berichten!'
    })

# Chat-Verlauf anzeigen
for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

# Chat-Input
prompt = st.chat_input('Stelle deine Frage zu den Controlling-Berichten...')

# Bei User Input
if prompt:
    # User-Nachricht anzeigen und speichern
    with st.chat_message('user'):
        st.markdown(prompt)
    st.session_state.messages.append({'role': 'user', 'content': prompt})

    # RAG-Antwort generieren
    with st.chat_message('assistant'):
        with st.spinner('🤔 Suche nach relevanten Informationen...'):
            try:
                # RAG-Query ausführen
                response = rag_agent.query(prompt, n_results=config.RAG_N_RESULTS, max_tokens=config.CLAUDE_MAX_TOKENS)

                # Antwort anzeigen
                st.markdown(response)

                # Antwort speichern
                st.session_state.messages.append({
                    'role': 'assistant',
                    'content': response
                })

            except Exception as e:
                error_msg = f"❌ Fehler bei der Anfrage: {e}"
                st.error(error_msg)
                st.exception(e)  # Zeigt den vollständigen Fehler
                st.session_state.messages.append({
                    'role': 'assistant',
                    'content': error_msg
                })