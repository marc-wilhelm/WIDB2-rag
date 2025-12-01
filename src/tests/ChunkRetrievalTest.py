"""
Test-Script für Chunk Retrieval

Dieses Script testet, ob die Vektordatenbank die richtige Anzahl an Chunks zurückgibt.
"""

import os
from MarkdownCleaner import MarkdownCleaner
from VectoreStoreManager import VectorStoreManager
import config

def test_chunk_retrieval(vector_store: VectorStoreManager):
    """
    Testet die Chunk-Retrieval-Funktionalität der Vektordatenbank.

    Args:
        vector_store: Eine initialisierte VectorStoreManager-Instanz
    """
    test_queries = [
        "Welche Monate werden behandelt?",
        "Gib mir eine Übersicht",
        "Wie sind die Umsätze?",
    ]

    for query in test_queries:
        print(f"\n{'=' * 70}")
        print(f"Frage: {query}")
        print(f"{'=' * 70}")

        results = vector_store.query_vector_db(query, n_results=5)

        if results and 'documents' in results:
            actual_chunks = len(results['documents'][0])
            print(f"📊 Zurückgegebene Chunks: {actual_chunks} von 5")

            if actual_chunks < 5:
                print("⚠️ PROBLEM: Nicht alle Chunks wurden zurückgegeben!")
            else:
                print("✅ Alle 5 Chunks wurden zurückgegeben!")

            for i, meta in enumerate(results['metadatas'][0]):
                month = meta.get('month', 'N/A')
                heading = meta.get('heading', 'N/A')
                dist = results['distances'][0][i]
                print(f"  - Chunk {i + 1}: {month} / {heading[:40]}... (Distanz: {dist:.4f})")


if __name__ == "__main__":
    """
    Hauptprogramm: Initialisiert die Vektordatenbank und führt Tests durch.
    """

    # Konfiguration
    MARKDOWN_FILE_PATH = str(config.MARKDOWN_FILE)

    print("Initialisiere Test-Umgebung...")

    # 1. Markdown verarbeiten
    cleaner = MarkdownCleaner(markdown_path=MARKDOWN_FILE_PATH)
    cleaned_data = cleaner.get_cleaned_data()

    # 2. Vektordatenbank initialisieren und befüllen
    vector_store = VectorStoreManager(
        db_path=config.CHROMA_TEST_DB_PATH,  # ← Geändert
        collection_name=config.CHROMA_TEST_COLLECTION_NAME
    )
    vector_store.ingest_markdown_data(cleaned_data)

    # 3. Test ausführen
    print("\n" + "=" * 70)
    print("STARTE CHUNK RETRIEVAL TESTS")
    print("=" * 70)

    test_chunk_retrieval(vector_store)

    print("\n" + "=" * 70)
    print("TESTS ABGESCHLOSSEN")
    print("=" * 70)