# Schritt 5: RAG-Workflow mit interaktivem Modus

import os
import shutil
import sys
from datetime import datetime
from dotenv import load_dotenv
from MarkdownCleaner import MultiMarkdownCleaner
from VectoreStoreManager import VectorStoreManager
from Grafikplotter import grafik_plotten_dynamisch
from RagAgent import RAGAgent
import config

# Lade .env Datei
load_dotenv()

# Konfiguration
ANTHROPIC_API_KEY = config.ANTHROPIC_API_KEY

# Prüfe ob API-Key geladen wurde
if not ANTHROPIC_API_KEY:
    print("FEHLER: ANTHROPIC_API_KEY nicht gefunden!")
    print("Stelle sicher, dass die .env Datei existiert und ANTHROPIC_API_KEY enthaelt.")
    sys.exit(1)

print("API-Key geladen")

# WORKFLOW

# 1. Alte Datenbank umbenennen (statt löschen - funktioniert auch mit offenen Handles)
db_path = config.CHROMA_DB_PATH
if os.path.exists(db_path):
    print(f"\n=== Alte Datenbank gefunden: {db_path} ===")

    # Erstelle Backup-Name mit Timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = db_path.parent / f"chroma_db_backup_{timestamp}"

    try:
        print(f"Benenne um nach: {backup_path}")
        os.rename(db_path, backup_path)
        print("Alte Datenbank umbenannt (kann manuell geloescht werden)")
        print(f"Backup liegt unter: {backup_path}")
    except Exception as e:
        print(f"FEHLER beim Umbenennen: {e}")
        print("\nLOESUNG:")
        print("1. Schliesse Streamlit (Strg+C im Terminal)")
        print("2. Fuehre dieses Script erneut aus")
        sys.exit(1)

print("\n=== Erstelle neue Datenbank ===")

# 2. Markdown verarbeiten
print("\nVerarbeite Markdown-Dateien...")

markdown_configs = [
    {
        'path': str(config.MARKDOWN_FILE_HT),
        'source_id': 'hometech'
    },
    {
        'path': str(config.MARKDOWN_FILE_DS),
        'source_id': 'digital_solutions'
    }
]

# DEBUG: Prüfe ob Dateien existieren
print("\n=== DEBUG: Dateien ueberpruefen ===")
all_files_exist = True
for cfg in markdown_configs:
    exists = os.path.exists(cfg['path'])
    print(f"Quelle: {cfg['source_id']}")
    print(f"Pfad: {cfg['path']}")
    print(f"Existiert: {'JA' if exists else 'NEIN'}")

    if exists:
        with open(cfg['path'], 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"Dateigroesse: {len(content)} Zeichen")
            # Zähle ## Überschriften
            section_count = content.count('\n## ')
            print(f"Anzahl ## Abschnitte: {section_count}")
    else:
        print("WARNUNG: Datei nicht gefunden!")
        all_files_exist = False
    print()

if not all_files_exist:
    print("FEHLER: Nicht alle Markdown-Dateien gefunden!")
    print("Stelle sicher dass die Dateien im data/ Ordner existieren.")
    sys.exit(1)

# Verarbeite Markdown-Dateien
multi_cleaner = MultiMarkdownCleaner(markdown_configs)
cleaned_data = multi_cleaner.process_all()

print(f"OK: {len(cleaned_data)} Abschnitte aus {len(markdown_configs)} Dateien verarbeitet.")

# 3. Vektordatenbank neu erstellen und befüllen
print("\nInitialisiere neue Vektordatenbank...")

vector_store = VectorStoreManager(
    db_path=config.CHROMA_DB_PATH,
    collection_name="controlling_berichte"
)
vector_store.ingest_markdown_data(cleaned_data)

# Verifiziere dass Daten geladen wurden
chunk_count = vector_store.collection.count()
print(f"\nOK: Chroma DB erstellt mit {chunk_count} Chunks.")

print("\n=== ERFOLGREICH ABGESCHLOSSEN ===")
print("\nHinweis: Alte DB-Backups koennen manuell geloescht werden:")
print(f"Verzeichnis: {db_path.parent}")

# 3. RAG-Agent initialisieren
print("\nInitialisiere RAG-Agent...")
rag_agent = RAGAgent(
    vector_store=vector_store,
    api_key=ANTHROPIC_API_KEY,
    plot_function=grafik_plotten_dynamisch
)


# INTERAKTIVER MODUS
print("\n" + "="*70)
print("RAG-Agent bereit! (Zum Beenden 'exit' eingeben)")
print("="*70 + "\n")

while True:
    user_input = input("Deine Frage: ").strip()

    if user_input.lower() in ['exit', 'quit', 'q']:
        print("Auf Wiedersehen!")
        break

    if user_input.strip():
        rag_agent.query(user_input, n_results=config.RAG_N_RESULTS)

    print("\n" + "-"*70 + "\n")