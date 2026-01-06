import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.RagAgent import RAGAgent


class TestCreateContextPrompt:

    @pytest.fixture
    def mock_vector_store(self):
        """Erstellt einen gemockten VectorStoreManager für isolierte Tests."""
        mock = Mock()
        return mock

    @pytest.fixture
    def rag_agent(self, mock_vector_store):
        """Erstellt eine RAGAgent-Instanz mit gemocktem VectorStore."""
        return RAGAgent(vector_store=mock_vector_store, api_key="test-key")

    def test_context_formatting_with_results(self, rag_agent, mock_vector_store):
        """
        Prüft ob Dokumente mit Metadaten korrekt formatiert werden.
        Erwartet: Strukturierter Text mit Dokumentnummern, Überschriften und Inhalten.
        """
        mock_vector_store.query_vector_db.return_value = {
            'documents': [['Text über Januar 2023', 'Text über Februar 2023']],
            'metadatas': [[
                {'source': 'test', 'heading': 'Januar 2023: Test', 'month': 'Januar 2023', 'type': 'monatsbericht'},
                {'source': 'test', 'heading': 'Februar 2023: Test', 'month': 'Februar 2023', 'type': 'monatsbericht'}
            ]]
        }

        result = rag_agent.create_context_prompt("test query", n_results=2)

        assert "[Dokument 1]" in result
        assert "[Dokument 2]" in result
        assert "Januar 2023: Test" in result
        assert "Februar 2023: Test" in result
        assert "Text über Januar 2023" in result

    def test_context_formatting_no_results(self, rag_agent, mock_vector_store):
        """
        Prüft das Verhalten wenn die Vektordatenbank keine Ergebnisse liefert.
        Erwartet: Fallback-Nachricht dass keine Dokumente gefunden wurden.
        """
        mock_vector_store.query_vector_db.return_value = {}

        result = rag_agent.create_context_prompt("test query")

        assert result == "Keine relevanten Dokumente gefunden."

    def test_context_formatting_empty_documents(self, rag_agent, mock_vector_store):
        """
        Prüft das Verhalten bei leerer Dokumentliste.
        Erwartet: Fallback-Nachricht wie bei keinen Ergebnissen.
        """
        mock_vector_store.query_vector_db.return_value = {
            'documents': [[]],
            'metadatas': [[]]
        }

        result = rag_agent.create_context_prompt("test query")

        assert result == "Keine relevanten Dokumente gefunden."

    def test_metadata_with_missing_fields(self, rag_agent, mock_vector_store):
        """
        Prüft robustes Verhalten bei fehlenden Metadaten-Feldern.
        Erwartet: N/A als Fallback-Wert für fehlende Metadaten.
        """
        mock_vector_store.query_vector_db.return_value = {
            'documents': [['Test content']],
            'metadatas': [[{}]]
        }

        result = rag_agent.create_context_prompt("test query")

        assert "Quelle: N/A" in result
        assert "Überschrift: N/A" in result
        assert "Monat: N/A" in result
        assert "Typ: N/A" in result

    def test_n_results_parameter_passed(self, rag_agent, mock_vector_store):
        """
        Validiert dass der n_results Parameter korrekt an die Vektordatenbank weitergegeben wird.
        """
        mock_vector_store.query_vector_db.return_value = {'documents': [[]]}

        rag_agent.create_context_prompt("test query", n_results=10)

        mock_vector_store.query_vector_db.assert_called_once_with("test query", n_results=10)


class TestChatHistory:

    @pytest.fixture
    def mock_vector_store(self):
        """Erstellt einen gemockten VectorStoreManager für isolierte Tests."""
        mock = Mock()
        return mock

    @pytest.fixture
    def rag_agent(self, mock_vector_store):
        """Erstellt eine RAGAgent-Instanz mit gemocktem VectorStore."""
        return RAGAgent(vector_store=mock_vector_store, api_key="test-key")

    def test_format_chat_history_empty(self, rag_agent):
        """
        Prüft dass eine leere Chat-History einen leeren String zurückgibt.
        """
        result = rag_agent.format_chat_history([])
        assert result == ""

    def test_format_chat_history_with_messages(self, rag_agent):
        """
        Prüft dass Chat-History korrekt formatiert wird.
        Erwartet: Formatierte Nachrichten mit Rollen (Benutzer/Assistent).
        """
        chat_history = [
            {'role': 'user', 'content': 'Wie hoch waren die Umsätze?'},
            {'role': 'assistant', 'content': '222.606 Euro'},
            {'role': 'user', 'content': 'Und im Februar?'}
        ]

        result = rag_agent.format_chat_history(chat_history)

        assert "Bisheriger Chat-Verlauf:" in result
        assert "[Benutzer]: Wie hoch waren die Umsätze?" in result
        assert "[Assistent]: 222.606 Euro" in result
        assert "[Benutzer]: Und im Februar?" in result
        assert "Ende des Chat-Verlaufs" in result

    def test_format_chat_history_none(self, rag_agent):
        """
        Prüft dass None-Werte für chat_history einen leeren String zurückgeben.
        """
        result = rag_agent.format_chat_history(None)
        assert result == ""

    def test_query_without_chat_history(self, rag_agent, mock_vector_store):
        """
        Prüft dass query() ohne chat_history funktioniert (Rückwärtskompatibilität).
        Standard mode="single" sollte verwendet werden.
        """
        mock_vector_store.query_vector_db.return_value = {
            'documents': [['Test content']],
            'metadatas': [[{'source': 'test', 'heading': 'Test', 'month': None, 'type': 'test'}]]
        }

        # Mock für Anthropic Client
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Test response")]
        mock_client.messages.create.return_value = mock_response
        rag_agent.client = mock_client

        result = rag_agent.query("Test query", n_results=1)

        assert "Test response" in result

        # Prüfe dass kein Chat-Verlauf im Prompt ist
        call_args = mock_client.messages.create.call_args
        user_prompt = call_args[1]['messages'][0]['content']
        assert "Bisheriger Chat-Verlauf" not in user_prompt

    def test_query_single_mode_ignores_chat_history(self, rag_agent, mock_vector_store):
        """
        Prüft dass im mode="single" die Chat-History ignoriert wird.
        Erwartet: Chat-History wird nicht in den Prompt eingefügt.
        """
        mock_vector_store.query_vector_db.return_value = {
            'documents': [['Test content']],
            'metadatas': [[{'source': 'test', 'heading': 'Test', 'month': None, 'type': 'test'}]]
        }

        # Mock für Anthropic Client
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Single mode response")]
        mock_client.messages.create.return_value = mock_response
        rag_agent.client = mock_client

        chat_history = [
            {'role': 'user', 'content': 'Erste Frage'},
            {'role': 'assistant', 'content': 'Erste Antwort'}
        ]

        result = rag_agent.query("Test query", n_results=1, mode="single", chat_history=chat_history)

        assert "Single mode response" in result

        # Prüfe dass KEIN Chat-Verlauf im Prompt ist, obwohl übergeben
        call_args = mock_client.messages.create.call_args
        user_prompt = call_args[1]['messages'][0]['content']
        assert "Bisheriger Chat-Verlauf" not in user_prompt
        assert "Erste Frage" not in user_prompt

    def test_query_with_chat_history(self, rag_agent, mock_vector_store):
        """
        Prüft dass query() mit chat_history die History in den Prompt einbaut.
        Nur im mode="multi" sollte die History verwendet werden.
        """
        mock_vector_store.query_vector_db.return_value = {
            'documents': [['Test content']],
            'metadatas': [[{'source': 'test', 'heading': 'Test', 'month': None, 'type': 'test'}]]
        }

        # Mock für Anthropic Client
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Antwort mit Kontext")]
        mock_client.messages.create.return_value = mock_response
        rag_agent.client = mock_client

        chat_history = [
            {'role': 'user', 'content': 'Erste Frage'},
            {'role': 'assistant', 'content': 'Erste Antwort'}
        ]

        result = rag_agent.query("Zweite Frage", n_results=1, mode="multi", chat_history=chat_history)

        assert "Antwort mit Kontext" in result

        # Prüfe dass Chat-Verlauf im Prompt ist
        call_args = mock_client.messages.create.call_args
        user_prompt = call_args[1]['messages'][0]['content']
        assert "Bisheriger Chat-Verlauf" in user_prompt
        assert "Erste Frage" in user_prompt
        assert "Erste Antwort" in user_prompt
        assert "Zweite Frage" in user_prompt

    def test_query_multi_mode_with_empty_history(self, rag_agent, mock_vector_store):
        """
        Prüft dass mode="multi" auch mit leerer History funktioniert.
        """
        mock_vector_store.query_vector_db.return_value = {
            'documents': [['Test content']],
            'metadatas': [[{'source': 'test', 'heading': 'Test', 'month': None, 'type': 'test'}]]
        }

        # Mock für Anthropic Client
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Multi mode response")]
        mock_client.messages.create.return_value = mock_response
        rag_agent.client = mock_client

        result = rag_agent.query("Test query", n_results=1, mode="multi", chat_history=[])

        assert "Multi mode response" in result

        # Prüfe dass kein Chat-Verlauf im Prompt ist (weil leer)
        call_args = mock_client.messages.create.call_args
        user_prompt = call_args[1]['messages'][0]['content']
        assert "Bisheriger Chat-Verlauf" not in user_prompt