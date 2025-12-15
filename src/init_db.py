# Schritt 5: RAG-Workflow mit interaktivem Modus

import os
from dotenv import load_dotenv
from MarkdownCleaner import MultiMarkdownCleaner
from VectoreStoreManager import VectorStoreManager
from RagAgent import RAGAgent
import config

# Lade .env Datei ZUERST
load_dotenv()

# Konfiguration
#MARKDOWN_FILE_PATH = str(config.MARKDOWN_FILE_HT)  # ← Geändert
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


# ✅ DEBUG: Prüfe ob Dateien existieren
print("\n=== DEBUG: Dateien überprüfen ===")
for cfg in markdown_configs:
    exists = os.path.exists(cfg['path'])
    print(f"Quelle: {cfg['source_id']}")
    print(f"Pfad: {cfg['path']}")
    print(f"Existiert: {'✅ JA' if exists else '❌ NEIN'}")
    
    if exists:
        with open(cfg['path'], 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"Dateigröße: {len(content)} Zeichen")
            # Zähle ## Überschriften
            section_count = content.count('\n## ')
            print(f"Anzahl ## Abschnitte: {section_count}")
    print()



multi_cleaner = MultiMarkdownCleaner(markdown_configs)
cleaned_data = multi_cleaner.process_all()

print(f"{len(cleaned_data)} Abschnitte aus {len(markdown_configs)} Dateien verarbeitet.")

# 2. Vektordatenbank initialisieren und befüllen
print("\nInitialisiere Vektordatenbank...")

#Nur temporär: um alte Werte aus Chroma DB zu löschen und DB neu aufzusetzen, sonst wird neues zweites Markdown-Dokument nicht in DB mit aufgenommen
import shutil
db_path = config.CHROMA_DB_PATH
if os.path.exists(db_path):
    print(f"Lösche alte Datenbank: {db_path}")
    shutil.rmtree(db_path)
    print("Alte Datenbank gelöscht. Erstelle neue...")



vector_store = VectorStoreManager(
    db_path=config.CHROMA_DB_PATH,
    collection_name="controlling_berichte"
)
vector_store.ingest_markdown_data(cleaned_data)

print("Chroma DB erstellt ✅")