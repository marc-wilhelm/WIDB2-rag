import pytest
from pathlib import Path
import tempfile
import shutil
import sys
import gc

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.MarkdownCleaner import MarkdownCleaner, MultiMarkdownCleaner
from src.VectoreStoreManager import VectorStoreManager


class TestMarkdownToChromaDB:

    @pytest.fixture
    def temp_db_path(self):
        """Erstellt ein temporäres Verzeichnis für eine isolierte ChromaDB-Instanz."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        gc.collect()
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except PermissionError:
            pass

    @pytest.fixture
    def temp_markdown_file(self):
        """Erstellt eine temporäre Markdown-Datei mit realistischen BWA-Daten."""
        content = """# Geschäftsentwicklung

## Einleitung

Dies ist die Einleitung des Berichts.

## Januar 2023: Stabile Ausgangslage

Im Januar 2023 verzeichnete das Unternehmen Umsatzerlöse von 222.606 Euro.

## Februar 2023: Rückgang

Im Februar kam es zu einem Rückgang auf 212.215 Euro."""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name

        yield temp_path

        Path(temp_path).unlink()

    def test_ingest_and_query(self, temp_db_path, temp_markdown_file):
        """
        Testet die grundlegende Pipeline: Markdown → ChromaDB → Retrieval.
        Erwartet: Dokumente werden gespeichert und sind abrufbar.
        """
        cleaner = MarkdownCleaner(temp_markdown_file, source_identifier='test')
        data = cleaner.get_cleaned_data()

        vector_store = VectorStoreManager(
            db_path=temp_db_path,
            collection_name="test_collection"
        )
        vector_store.ingest_markdown_data(data)

        results = vector_store.query_vector_db("Umsatzerlöse Januar", n_results=2)

        assert 'documents' in results
        assert len(results['documents'][0]) > 0
        assert 'metadatas' in results
        assert 'distances' in results

        del vector_store.client
        gc.collect()

    def test_query_returns_relevant_documents(self, temp_db_path, temp_markdown_file):
        """
        Prüft ob semantisch relevante Dokumente zurückgegeben werden.
        Erwartet: Query "Januar 2023" findet Dokumente mit Januar-Bezug oder den Umsatzzahlen.
        """
        cleaner = MarkdownCleaner(temp_markdown_file, source_identifier='test')
        data = cleaner.get_cleaned_data()

        vector_store = VectorStoreManager(
            db_path=temp_db_path,
            collection_name="test_collection"
        )
        vector_store.ingest_markdown_data(data)

        results = vector_store.query_vector_db("Januar 2023", n_results=2)

        assert len(results['documents'][0]) > 0

        all_docs = " ".join(results['documents'][0])
        assert "222.606" in all_docs or "Januar" in all_docs or "2023" in all_docs

        del vector_store.client
        gc.collect()

    def test_metadata_preserved(self, temp_db_path, temp_markdown_file):
        """
        Validiert dass Metadaten (Quelle, Überschrift, Monat, Typ) nach dem Speichern erhalten bleiben.
        """
        cleaner = MarkdownCleaner(temp_markdown_file, source_identifier='finance')
        data = cleaner.get_cleaned_data()

        vector_store = VectorStoreManager(
            db_path=temp_db_path,
            collection_name="test_collection"
        )
        vector_store.ingest_markdown_data(data)

        results = vector_store.query_vector_db("Januar", n_results=1)

        metadata = results['metadatas'][0][0]
        assert metadata['source'] == 'finance'
        assert 'heading' in metadata
        assert 'month' in metadata
        assert 'type' in metadata

        del vector_store.client
        gc.collect()

    def test_empty_data_handling(self, temp_db_path):
        """
        Prüft robustes Verhalten bei leerer Datenliste.
        Erwartet: Keine Fehler, leere Ergebnisse bei Query.
        """
        vector_store = VectorStoreManager(
            db_path=temp_db_path,
            collection_name="test_collection"
        )

        vector_store.ingest_markdown_data([])

        results = vector_store.query_vector_db("test", n_results=1)
        assert results == {} or results['documents'][0] == []

        del vector_store.client
        gc.collect()

    def test_multiple_sources(self, temp_db_path):
        """
        Testet dass mehrere Markdown-Dateien (Multi-Source) korrekt verarbeitet werden.
        Erwartet: Beide Sources sind in den Metadaten identifizierbar.
        """
        content1 = """# Doc 1
## Einleitung
Text 1
## Januar 2023: Test
Content 1"""

        content2 = """# Doc 2
## Einleitung
Text 2
## Februar 2024: Test
Content 2"""

        files = []
        for content in [content1, content2]:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
                f.write(content)
                files.append(f.name)

        try:
            configs = [
                {'path': files[0], 'source_id': 'source1'},
                {'path': files[1], 'source_id': 'source2'}
            ]

            multi_cleaner = MultiMarkdownCleaner(configs)
            data = multi_cleaner.process_all()

            vector_store = VectorStoreManager(
                db_path=temp_db_path,
                collection_name="test_collection"
            )
            vector_store.ingest_markdown_data(data)

            results = vector_store.query_vector_db("Test", n_results=4)

            sources = [meta['source'] for meta in results['metadatas'][0]]
            assert 'source1' in sources
            assert 'source2' in sources

            del vector_store.client
            gc.collect()

        finally:
            for f in files:
                Path(f).unlink()


class TestVectorStoreErrorHandling:

    @pytest.fixture
    def temp_db_path(self):
        """Erstellt ein temporäres Verzeichnis für ChromaDB."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        gc.collect()
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except PermissionError:
            pass

    def test_data_with_empty_text(self, temp_db_path):
        """
        Prüft dass Einträge mit leerem Text ignoriert werden.
        Erwartet: Nur Einträge mit Text werden gespeichert und gefunden.
        """
        vector_store = VectorStoreManager(
            db_path=temp_db_path,
            collection_name="test_collection"
        )

        data = [
            {'text': '', 'source': 'test', 'heading': 'Test', 'month': None, 'type': 'test', 'paragraph_id': 0},
            {'text': 'Valid text', 'source': 'test', 'heading': 'Test', 'month': None, 'type': 'test', 'paragraph_id': 1}
        ]

        vector_store.ingest_markdown_data(data)

        results = vector_store.query_vector_db("Valid", n_results=1)
        assert len(results['documents'][0]) == 1

        del vector_store.client
        gc.collect()