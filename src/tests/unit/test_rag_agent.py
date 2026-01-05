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