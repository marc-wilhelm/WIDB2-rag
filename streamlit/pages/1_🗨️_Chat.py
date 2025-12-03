import streamlit as st
import sys
from pathlib import Path

# Füge src/ zum Python-Pfad hinzu
# Von streamlit/pages/ aus: ../../src/
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent  # Zwei Ebenen hoch = Root
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from MarkdownCleaner import MarkdownCleaner
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

st.title("🤖 RAG Chatbot für BWA-Analyse")
st.markdown("Stelle Fragen zu den Controlling-Berichten und erhalte präzise Antworten basierend auf den Dokumenten.")


# Initialisierung des RAG-Systems (nur einmal beim ersten Laden)
@st.cache_resource
def initialize_rag_system():
    """
    Initialisiert das RAG-System (wird nur einmal ausgeführt und dann gecacht).
    """
    try:
        # API-Key laden
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            st.error("❌ ANTHROPIC_API_KEY nicht in .env gefunden!")
            st.stop()

        # Pfade (relativ zum Projekt-Root)
        markdown_file = config.MARKDOWN_FILE

        if not markdown_file.exists():
            st.error(f"❌ Markdown-Datei nicht gefunden: {markdown_file}")
            st.stop()

        with st.spinner("🔄 Initialisiere RAG-System..."):
            # 1. Markdown verarbeiten
            cleaner = MarkdownCleaner(markdown_path=str(markdown_file))
            cleaned_data = cleaner.get_cleaned_data()

            # 2. Vektordatenbank initialisieren
            vector_store = VectorStoreManager()
            vector_store.ingest_markdown_data(cleaned_data)

            # 3. RAG-Agent initialisieren
            rag_agent = RAGAgent(
                vector_store=vector_store,
                api_key=api_key
            )

            return rag_agent, len(cleaned_data)

    except Exception as e:
        st.error(f"❌ Fehler bei der Initialisierung: {e}")
        st.exception(e)  # Zeigt den vollständigen Fehler
        st.stop()


# RAG-System laden
rag_agent, num_documents = initialize_rag_system()

# Erfolgreiche Initialisierung anzeigen
with st.sidebar:
    st.success("✅ RAG-System bereit")
    st.info(f"📄 {num_documents} Chunks geladen")
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