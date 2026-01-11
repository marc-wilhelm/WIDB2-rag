from RagAgent import RAGAgent
from Grafikplotter import grafik_plotten_dynamisch,RAGPlotPipeline
from VectoreStoreManager import VectorStoreManager
import config


import os
import shutil
import sys
from datetime import datetime
from dotenv import load_dotenv
from MarkdownCleaner import MultiMarkdownCleaner

# Lade .env Datei
load_dotenv()

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

# Verarbeite Markdown-Dateien
multi_cleaner = MultiMarkdownCleaner(markdown_configs)
cleaned_data = multi_cleaner.process_all()

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


# 1. RAG-Agent initialisieren
rag_agent = RAGAgent(
    vector_store=vector_store,
    api_key=config.ANTHROPIC_API_KEY
)

# 2. Pipeline mit Plot-Funktion erstellen
pipeline = RAGPlotPipeline(
    rag_agent=rag_agent,
    plot_function=grafik_plotten_dynamisch
)

# 3. Anfrage mit Plot
result = pipeline.process_query(
    user_question="Zeige mir die Umsatzentwicklung von HomeTech über die letzten Monate als Diagramm",
    mode="single",
    animate=True  # Animation aktivieren
)

# 4. Ergebnis verarbeiten
print("\n" + "="*70)
print("ANTWORT:")
print(result['answer'])
print("="*70)

if result['plot_created']:
    print("\n✓ Plot wurde erstellt!")
    print(f"Plot-Daten: {result['plot_data']}")
    # result['plot_result'] enthält die Figure oder HTML-Animation
else:
    print("\n○ Kein Plot erstellt")


# Beispiel 2: Mehrere Units vergleichen
result2 = pipeline.process_query(
    user_question="Vergleiche die Verkaufszahlen von HomeTech und DigitalSolutions",
    animate=False  # Statischer Plot
)


# Beispiel 3: Ohne Plot (normale RAG-Anfrage)
result3 = pipeline.process_query(
    user_question="Was sind die Hauptprodukte von HomeTech?"
)
# Dieser erstellt keinen Plot, da keine Plot-Keywords in der Frage


# ============================================
# ALTERNATIVE: Direkter Aufruf ohne Pipeline
# ============================================

def quick_plot_query(rag_agent, user_question: str, animate: bool = True):
    """
    Schnelle Funktion für Plot-Anfragen ohne Pipeline-Objekt
    """
    pipeline = RAGPlotPipeline(rag_agent, grafik_plotten_dynamisch)
    return pipeline.process_query(user_question, animate=animate)


# Verwendung:
# result = quick_plot_query(rag_agent, "Zeige Umsatztrend", animate=True)