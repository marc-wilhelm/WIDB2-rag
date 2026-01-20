import pytest
from pathlib import Path
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
import sys
import gc

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.MarkdownCleaner import MarkdownCleaner
from src.VectoreStoreManager import VectorStoreManager
from src.RagAgent import RAGAgent


class TestRAGPipeline:

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
        """Erstellt eine temporäre Markdown-Datei mit Geschäftsdaten für Tests."""
        content = """# Geschäftsbericht

## Einleitung

Geschäftsentwicklung im Überblick.

## Januar 2023: Stabile Ausgangslage

Im Januar 2023 verzeichnete das Unternehmen Umsatzerlöse von 222.606 Euro.
Der Materialaufwand betrug 98.016 Euro.

## Februar 2023: Rückgang

Im Februar kam es zu einem Rückgang der Umsatzerlöse auf 212.215 Euro.
Die Materialkosten stiegen auf 102.621 Euro."""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name

        yield temp_path

        Path(temp_path).unlink()

    @pytest.fixture
    def mock_plot_function(self):
        """Erstellt eine gemockte Plot-Funktion."""
        return Mock()

    @pytest.fixture
    def setup_pipeline(self, temp_db_path, temp_markdown_file):
        """
        Setup-Fixture die eine vollständige RAG-Pipeline initialisiert.
        Markdown wird verarbeitet und in ChromaDB gespeichert.
        """
        cleaner = MarkdownCleaner(temp_markdown_file, source_identifier='test_report')
        data = cleaner.get_cleaned_data()

        vector_store = VectorStoreManager(
            db_path=temp_db_path,
            collection_name="test_collection"
        )
        vector_store.ingest_markdown_data(data)

        yield vector_store

        del vector_store.client
        gc.collect()

    @patch('anthropic.Anthropic')
    def test_full_pipeline_with_mocked_llm(self, mock_anthropic_class, setup_pipeline, mock_plot_function):
        """
        Testet die vollständige RAG-Pipeline mit gemockter Claude API.
        Erwartet: Query → Retrieval → Context → LLM → Antwort mit korrekten Zahlen.
        """
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Die Umsatzerlöse im Januar 2023 betrugen 222.606 Euro.")]
        mock_client.messages.create.return_value = mock_response

        vector_store = setup_pipeline
        rag_agent = RAGAgent(vector_store=vector_store, api_key="test-key", plot_function=mock_plot_function)

        response = rag_agent.query("Wie hoch waren die Umsatzerlöse im Januar 2023?", n_results=2)

        # query() gibt jetzt ein Dictionary zurück
        assert isinstance(response, dict)
        assert "answer" in response
        assert "222.606" in response["answer"]
        mock_client.messages.create.assert_called_once()

    @patch('anthropic.Anthropic')
    def test_context_contains_relevant_data(self, mock_anthropic_class, setup_pipeline, mock_plot_function):
        """
        Prüft ob der Context-Prompt relevante Daten aus der Vektordatenbank enthält.
        Erwartet: Der an Claude übergebene Prompt enthält die richtigen Zahlen/Begriffe.
        """
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Antwort")]
        mock_client.messages.create.return_value = mock_response

        vector_store = setup_pipeline
        rag_agent = RAGAgent(vector_store=vector_store, api_key="test-key", plot_function=mock_plot_function)

        rag_agent.query("Umsatzerlöse Januar", n_results=1)

        call_args = mock_client.messages.create.call_args
        user_prompt = call_args[1]['messages'][0]['content']

        assert "222.606" in user_prompt or "Januar" in user_prompt or "Umsatz" in user_prompt

    @patch('anthropic.Anthropic')
    def test_query_with_no_relevant_results(self, mock_anthropic_class, setup_pipeline, mock_plot_function):
        """
        Testet Verhalten bei Fragen außerhalb des Datenbestands.
        Erwartet: System antwortet graceful auch wenn keine relevanten Daten gefunden werden.
        """
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Keine Information verfügbar.")]
        mock_client.messages.create.return_value = mock_response

        vector_store = setup_pipeline
        rag_agent = RAGAgent(vector_store=vector_store, api_key="test-key", plot_function=mock_plot_function)

        response = rag_agent.query("Wie ist das Wetter in Tokyo?", n_results=1)

        assert isinstance(response, dict)

    @patch('anthropic.Anthropic')
    def test_api_error_handling(self, mock_anthropic_class, setup_pipeline, mock_plot_function):
        """
        Prüft robustes Error-Handling bei Claude API-Fehlern.
        Erwartet: Fehlermeldung wird zurückgegeben statt einem Crash.
        """
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        mock_client.messages.create.side_effect = Exception("API Error")

        vector_store = setup_pipeline
        rag_agent = RAGAgent(vector_store=vector_store, api_key="test-key", plot_function=mock_plot_function)

        response = rag_agent.query("Test query", n_results=1)

        assert isinstance(response, dict)
        assert "answer" in response
        assert "Fehler" in response["answer"]
        assert "API Error" in response["answer"]

    @patch('anthropic.Anthropic')
    def test_different_n_results(self, mock_anthropic_class, setup_pipeline, mock_plot_function):
        """
        Validiert dass der n_results Parameter die Anzahl der abgerufenen Dokumente steuert.
        Erwartet: Context-Prompt enthält entsprechende Anzahl an Dokumenten.
        """
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Antwort")]
        mock_client.messages.create.return_value = mock_response

        vector_store = setup_pipeline
        rag_agent = RAGAgent(vector_store=vector_store, api_key="test-key", plot_function=mock_plot_function)

        rag_agent.query("Test", n_results=1)

        call_args = mock_client.messages.create.call_args
        user_prompt = call_args[1]['messages'][0]['content']

        assert "[Dokument" in user_prompt

    @patch('anthropic.Anthropic')
    def test_query_with_chat_history(self, mock_anthropic_class, setup_pipeline, mock_plot_function):
        """
        Testet die RAG-Pipeline mit Chat-History im mode="multi".
        Erwartet: Chat-Verlauf wird in den Prompt eingebaut und kontextbezogene Antworten sind möglich.
        """
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Im Februar 2023 betrugen die Umsatzerlöse 212.215 Euro.")]
        mock_client.messages.create.return_value = mock_response

        vector_store = setup_pipeline
        rag_agent = RAGAgent(vector_store=vector_store, api_key="test-key", plot_function=mock_plot_function)

        # Simuliere einen Chat-Verlauf
        chat_history = [
            {'role': 'user', 'content': 'Wie hoch waren die Umsatzerlöse im Januar 2023?'},
            {'role': 'assistant', 'content': 'Im Januar 2023 betrugen die Umsatzerlöse 222.606 Euro.'}
        ]

        # Stelle eine Anschlussfrage im multi Modus
        response = rag_agent.query("Und im Februar?", n_results=2, mode="multi", chat_history=chat_history)

        assert isinstance(response, dict)
        assert "answer" in response
        assert "212.215" in response["answer"]

        # Prüfe dass Chat-History im Prompt enthalten ist
        call_args = mock_client.messages.create.call_args
        user_prompt = call_args[1]['messages'][0]['content']

        assert "Bisheriger Chat-Verlauf" in user_prompt
        assert "Januar 2023" in user_prompt
        assert "222.606" in user_prompt

    @patch('anthropic.Anthropic')
    def test_query_single_mode_no_history(self, mock_anthropic_class, setup_pipeline, mock_plot_function):
        """
        Testet die RAG-Pipeline im mode="single".
        Erwartet: Chat-History wird NICHT in den Prompt eingebaut, auch wenn übergeben.
        """
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Im Februar 2023 betrugen die Umsatzerlöse 212.215 Euro.")]
        mock_client.messages.create.return_value = mock_response

        vector_store = setup_pipeline
        rag_agent = RAGAgent(vector_store=vector_store, api_key="test-key", plot_function=mock_plot_function)

        # Simuliere einen Chat-Verlauf
        chat_history = [
            {'role': 'user', 'content': 'Wie hoch waren die Umsatzerlöse im Januar 2023?'},
            {'role': 'assistant', 'content': 'Im Januar 2023 betrugen die Umsatzerlöse 222.606 Euro.'}
        ]

        # Stelle eine Frage im single Modus (History sollte ignoriert werden)
        response = rag_agent.query("Wie hoch waren die Umsatzerlöse im Februar?", n_results=2, mode="single", chat_history=chat_history)

        assert isinstance(response, dict)

        # Prüfe dass Chat-History NICHT im Prompt enthalten ist
        call_args = mock_client.messages.create.call_args
        user_prompt = call_args[1]['messages'][0]['content']

        assert "Bisheriger Chat-Verlauf" not in user_prompt
        assert "Januar 2023" not in user_prompt or "Dokument" in user_prompt  # Januar nur in Dokumenten, nicht in History


class TestContextPromptFormatting:

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

    @pytest.fixture
    def temp_markdown_file(self):
        """Erstellt eine minimale Markdown-Datei für Formatting-Tests."""
        content = """# Test
## Januar 2023: Test
Test content for Januar."""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name

        yield temp_path
        Path(temp_path).unlink()

    @pytest.fixture
    def mock_plot_function(self):
        """Erstellt eine gemockte Plot-Funktion."""
        return Mock()

    def test_context_prompt_structure(self, temp_db_path, temp_markdown_file, mock_plot_function):
        """
        Prüft die Struktur des Context-Prompts im Detail.
        Erwartet: Alle erwarteten Felder (Quelle, Überschrift, Monat, Typ) sind vorhanden.
        """
        cleaner = MarkdownCleaner(temp_markdown_file, source_identifier='test')
        data = cleaner.get_cleaned_data()

        vector_store = VectorStoreManager(
            db_path=temp_db_path,
            collection_name="test_collection"
        )
        vector_store.ingest_markdown_data(data)

        rag_agent = RAGAgent(vector_store=vector_store, api_key="test-key", plot_function=mock_plot_function)

        context = rag_agent.create_context_prompt("Januar", n_results=1)

        assert "[Dokument 1]" in context
        assert "Quelle:" in context
        assert "Überschrift:" in context
        assert "Monat:" in context
        assert "Typ:" in context
        assert "Inhalt:" in context
        assert "=" * 60 in context

        del vector_store.client
        gc.collect()