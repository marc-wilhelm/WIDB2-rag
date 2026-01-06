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

# Beispiel-Fragen in einem ausklappbaren Bereich
with st.expander("💡 Beispiel-Fragen", expanded=False):
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
            st.info("💡 Bitte führe zuerst `python src/init_db.py` aus, um die Datenbank zu erstellen.")
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


# RAG-System laden
rag_agent, num_chunks = initialize_rag_system()

# Erfolgreiche Initialisierung anzeigen
with st.sidebar:
    st.markdown("### Status")
    db_exists = config.CHROMA_DB_PATH.exists()

    if db_exists:
        st.success("✅ Datenbank vorhanden")
    else:
        st.error("❌ Keine Datenbank gefunden")
        st.info("**Datenbank erstellen:**")
        st.code("python src/init_db.py", language="bash")
        st.stop()

    st.info(f"📄 {num_chunks} Chunks geladen")

    if num_chunks > 0:
        st.success("✅ RAG-System bereit")
    else:
        st.error("❌ RAG-System nicht bereit")

    st.markdown("---")

    # Modus-Auswahl
    st.markdown("### 🔧 Chat-Einstellungen")
    chat_mode = st.selectbox(
        "Wähle den Chat-Modus:",
        options=["single", "multi"],
        format_func=lambda x: "Single (ohne Chat-Verlauf)" if x == "single" else "Multi (mit Chat-Verlauf)"
    )

    if chat_mode == "single":
        st.info("**Single-Modus**: Jede Frage wird unabhängig beantwortet.")
    else:
        st.info("**Multi-Modus**: Chat-Verlauf wird für Kontext genutzt.")

    # Button zum Löschen des Chats
    if st.button("🗑️ Chatverlauf löschen"):
        st.session_state.messages = []
        st.rerun()

# Sidebar-Kontrollen für DB-Verwaltung
with st.sidebar:
    st.markdown("---")
    st.markdown("### 🗄️ Datenbank neu initialisieren")
    st.info("""
    1. Stoppe Streamlit (Strg+C im Terminal)
    2. Führe den folgenden Befehl aus: `python src/init_db.py`
    3. Starte Streamlit neu: `streamlit run streamlit/Home.py`
    """)

# Chat-Verlauf initialisieren
if 'messages' not in st.session_state:
    st.session_state.messages = []
    # Begrüßungsnachricht
    st.session_state.messages.append({
        'role': 'assistant',
        'content': 'Hallo! Ich bin dein RAG-Assistent für BWA-Analysen. Stelle mir Fragen zu den Controlling-Berichten!'
    })

# Processing-State initialisieren
if 'is_processing' not in st.session_state:
    st.session_state.is_processing = False

# Chat-Verlauf anzeigen
for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

# Chat-Input (disabled während Verarbeitung)
prompt = st.chat_input(
    'Stelle deine Frage zu den Controlling-Berichten...',
    disabled=st.session_state.is_processing
)

# Bei User Input
if prompt and not st.session_state.is_processing:
    # Setze processing flag
    st.session_state.is_processing = True

    # User-Nachricht speichern
    st.session_state.messages.append({'role': 'user', 'content': prompt})

    # Rerun um die Nachricht aus dem Loop anzuzeigen
    st.rerun()

# Verarbeite die letzte Nachricht wenn processing aktiv ist
if st.session_state.is_processing:
    last_message = st.session_state.messages[-1]

    # Prüfe ob die letzte Nachricht vom User ist (noch nicht verarbeitet)
    if last_message['role'] == 'user':
        # RAG-Antwort generieren
        with st.chat_message('assistant'):
            with st.spinner('🤔 Suche nach relevanten Informationen...'):
                try:
                    # Chat-History vorbereiten (nur im multi Modus)
                    if chat_mode == "multi":
                        # Chat-History vorbereiten (ohne die aktuelle Frage und ohne Begrüßung)
                        chat_history = [
                            msg for msg in st.session_state.messages[:-1]  # Aktuelle Frage ausschließen
                            if not (msg['role'] == 'assistant' and 'Hallo!' in msg['content'])  # Begrüßung ausschließen
                        ]
                    else:
                        chat_history = None

                    # RAG-Query ausführen mit Modus
                    response = rag_agent.query(
                        last_message['content'],
                        n_results=config.RAG_N_RESULTS,
                        max_tokens=config.CLAUDE_MAX_TOKENS,
                        mode=chat_mode,
                        chat_history=chat_history
                    )

                    # Antwort speichern
                    st.session_state.messages.append({
                        'role': 'assistant',
                        'content': response
                    })

                except Exception as e:
                    error_msg = f"❌ Fehler bei der Anfrage: {e}"
                    st.exception(e)
                    st.session_state.messages.append({
                        'role': 'assistant',
                        'content': error_msg
                    })

        # Reset processing flag und rerun
        st.session_state.is_processing = False
        st.rerun()