# Schritt 5: RAG-Workflow mit interaktivem Modus

import os
from dotenv import load_dotenv
from MarkdownCleaner import MarkdownCleaner
from VectoreStoreManager import VectorStoreManager
from RagAgent import RAGAgent
import config

# Lade .env Datei ZUERST
load_dotenv()

# Konfiguration
MARKDOWN_FILE_PATH = str(config.MARKDOWN_FILE)  # ← Geändert
ANTHROPIC_API_KEY = config.ANTHROPIC_API_KEY

# Prüfe ob API-Key geladen wurde
if not ANTHROPIC_API_KEY:
    print("FEHLER: ANTHROPIC_API_KEY nicht gefunden!")
    print("Stelle sicher, dass die .env Datei existiert und ANTHROPIC_API_KEY enthält.")
    exit(1)

print(f"API-Key geladen")

# WORKFLOW

# 1. Markdown verarbeiten
print("\nVerarbeite Markdown-Datei...")
cleaner = MarkdownCleaner(markdown_path=MARKDOWN_FILE_PATH)
cleaned_data = cleaner.get_cleaned_data()
print(f"{len(cleaned_data)} Abschnitte verarbeitet.")

# 2. Vektordatenbank initialisieren und befüllen
print("\nInitialisiere Vektordatenbank...")
vector_store = VectorStoreManager(
    db_path="./chroma_db",
    collection_name="controlling_berichte"
)
vector_store.ingest_markdown_data(cleaned_data)

# 3. RAG-Agent initialisieren
print("\nInitialisiere RAG-Agent...")
rag_agent = RAGAgent(
    vector_store=vector_store,
    api_key=ANTHROPIC_API_KEY
)


# INTERAKTIVER MODUS
print("\n" + "="*70)
print("RAG-Agent bereit! (Zum Beenden 'exit' eingeben)")
print("="*70 + "\n")

while True:
    user_input = input("Deine Frage: ")

    if user_input.lower() in ['exit', 'quit', 'q']:
        print("Auf Wiedersehen!")
        break

    if user_input.strip():
        rag_agent.query(user_input, n_results=5)

    print("\n" + "-"*70 + "\n")