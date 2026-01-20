import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
import sys
import json

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.RagAgent import RAGAgent


class TestCreateContextPrompt:

    @pytest.fixture
    def mock_vector_store(self):
        """Erstellt einen gemockten VectorStoreManager für isolierte Tests."""
        mock = Mock()
        return mock

    @pytest.fixture
    def mock_plot_function(self):
        """Erstellt eine gemockte Plot-Funktion."""
        return Mock()

    @pytest.fixture
    def rag_agent(self, mock_vector_store, mock_plot_function):
        """Erstellt eine RAGAgent-Instanz mit gemocktem VectorStore und Plot-Funktion."""
        return RAGAgent(vector_store=mock_vector_store, api_key="test-key", plot_function=mock_plot_function)

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
    def mock_plot_function(self):
        """Erstellt eine gemockte Plot-Funktion."""
        return Mock()

    @pytest.fixture
    def rag_agent(self, mock_vector_store, mock_plot_function):
        """Erstellt eine RAGAgent-Instanz mit gemocktem VectorStore und Plot-Funktion."""
        return RAGAgent(vector_store=mock_vector_store, api_key="test-key", plot_function=mock_plot_function)

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

        # query() gibt jetzt ein Dictionary zurück
        assert isinstance(result, dict)
        assert "answer" in result
        assert "Test response" in result["answer"]

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

        # query() gibt jetzt ein Dictionary zurück
        assert isinstance(result, dict)
        assert "answer" in result
        assert "Single mode response" in result["answer"]

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

        # query() gibt jetzt ein Dictionary zurück
        assert isinstance(result, dict)
        assert "answer" in result
        assert "Antwort mit Kontext" in result["answer"]

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

        # query() gibt jetzt ein Dictionary zurück
        assert isinstance(result, dict)
        assert "answer" in result
        assert "Multi mode response" in result["answer"]

        # Prüfe dass kein Chat-Verlauf im Prompt ist (weil leer)
        call_args = mock_client.messages.create.call_args
        user_prompt = call_args[1]['messages'][0]['content']
        assert "Bisheriger Chat-Verlauf" not in user_prompt


class TestShouldCreatePlot:
    """Tests für die Plot-Keyword-Erkennung."""

    @pytest.fixture
    def mock_vector_store(self):
        return Mock()

    @pytest.fixture
    def mock_plot_function(self):
        return Mock()

    @pytest.fixture
    def rag_agent(self, mock_vector_store, mock_plot_function):
        return RAGAgent(vector_store=mock_vector_store, api_key="test-key", plot_function=mock_plot_function)

    def test_should_create_plot_with_plot_keyword(self, rag_agent):
        """Erkennt 'plotte' Keyword."""
        assert rag_agent._should_create_plot("Plotte die Umsätze") is True

    def test_should_create_plot_with_diagramm_keyword(self, rag_agent):
        """Erkennt 'diagramm' Keyword."""
        assert rag_agent._should_create_plot("Erstelle ein Diagramm") is True

    def test_should_create_plot_with_grafik_keyword(self, rag_agent):
        """Erkennt 'grafik' Keyword."""
        assert rag_agent._should_create_plot("Zeige eine Grafik") is True

    def test_should_create_plot_with_visualisierung_keyword(self, rag_agent):
        """Erkennt 'visualisier' Keyword."""
        assert rag_agent._should_create_plot("Visualisiere die Entwicklung") is True

    def test_should_create_plot_with_trend_keyword(self, rag_agent):
        """Erkennt 'trend' Keyword."""
        assert rag_agent._should_create_plot("Zeige den Trend") is True

    def test_should_create_plot_no_keyword(self, rag_agent):
        """Keine Plot-Keywords vorhanden."""
        assert rag_agent._should_create_plot("Wie hoch waren die Umsätze?") is False

    def test_should_create_plot_case_insensitive(self, rag_agent):
        """Plot-Erkennung ist case-insensitive."""
        assert rag_agent._should_create_plot("PLOTTE DIE DATEN") is True
        assert rag_agent._should_create_plot("Plotte die Daten") is True
        assert rag_agent._should_create_plot("plotte die daten") is True


class TestExtractHelper:
    """Tests für die Extraktion von Business Units und Monaten."""

    @pytest.fixture
    def mock_vector_store(self):
        return Mock()

    @pytest.fixture
    def mock_plot_function(self):
        return Mock()

    @pytest.fixture
    def rag_agent(self, mock_vector_store, mock_plot_function):
        return RAGAgent(vector_store=mock_vector_store, api_key="test-key", plot_function=mock_plot_function)

    def test_extract_single_month(self, rag_agent):
        """Extrahiert einzelnen Monat."""
        units, months = rag_agent._extract_helper("Umsätze im Januar")
        assert "januar" in months
        assert len(months) == 1

    def test_extract_multiple_months(self, rag_agent):
        """Extrahiert mehrere Monate."""
        units, months = rag_agent._extract_helper("Entwicklung von Januar bis März")
        assert "januar" in months
        assert "märz" in months
        assert len(months) == 2

    def test_extract_hometech_unit(self, rag_agent):
        """Extrahiert Home Tech Business Unit."""
        units, months = rag_agent._extract_helper("Home Tech Umsätze")
        assert "hometech" in units

    def test_extract_hometech_unit_with_hyphen(self, rag_agent):
        """Extrahiert Home Tech mit Bindestrich."""
        units, months = rag_agent._extract_helper("Home-Tech Performance")
        assert "hometech" in units

    def test_extract_digital_solutions_unit(self, rag_agent):
        """Extrahiert Digital Solutions Business Unit."""
        units, months = rag_agent._extract_helper("Digital Solutions Performance")
        assert "digital_solutions" in units

    def test_extract_digital_solutions_singular(self, rag_agent):
        """Extrahiert Digital Solution (Singular)."""
        units, months = rag_agent._extract_helper("Digital Solution Bericht")
        assert "digital_solutions" in units

    def test_extract_both_units_explicit(self, rag_agent):
        """Extrahiert beide Units bei 'beide Business Units'."""
        units, months = rag_agent._extract_helper("Vergleich beide Business Units")
        assert "hometech" in units
        assert "digital_solutions" in units
        assert len(units) == 2

    def test_extract_both_units_alle_variant(self, rag_agent):
        """Extrahiert beide Units bei 'alle Business Units'."""
        units, months = rag_agent._extract_helper("alle Business Units")
        assert "hometech" in units
        assert "digital_solutions" in units
        assert len(units) == 2

    def test_extract_all_months_with_quartal(self, rag_agent):
        """Extrahiert alle Monate bei 'entwicklung quartal' (Regex-Pattern)."""
        units, months = rag_agent._extract_helper("entwicklung quartal")
        assert len(months) == 12

    def test_extract_all_months_with_zeitraum(self, rag_agent):
        """Extrahiert alle Monate bei 'alle zeitraum' (Regex-Pattern)."""
        units, months = rag_agent._extract_helper("alle zeitraum")
        assert len(months) == 12

    def test_extract_all_months_with_monat_singular(self, rag_agent):
        """Extrahiert alle Monate bei 'entwicklung monat' - Singular! (Regex-Pattern)."""
        units, months = rag_agent._extract_helper("entwicklung monat")
        assert len(months) == 12

    def test_extract_no_units_no_months(self, rag_agent):
        """Keine Units oder Monate im Text."""
        units, months = rag_agent._extract_helper("Was ist die Strategie?")
        assert len(units) == 0
        assert len(months) == 0

    def test_extract_case_insensitive(self, rag_agent):
        """Extraktion ist case-insensitive."""
        units, months = rag_agent._extract_helper("JANUAR und HOME TECH")
        assert "januar" in months
        assert "hometech" in units

    def test_extract_with_multiple_arguments(self, rag_agent):
        """Funktion nimmt *query - testet mehrere Argumente."""
        units, months = rag_agent._extract_helper("Januar", "Home Tech", "Februar")
        assert "januar" in months
        assert "februar" in months
        assert "hometech" in units
        assert len(months) == 2

    def test_extract_deduplication(self, rag_agent):
        """Duplikate werden entfernt durch set()."""
        units, months = rag_agent._extract_helper("Januar Home Tech", "Januar Digital Solutions")
        assert len(months) == 1  # Januar nur einmal
        assert "januar" in months
        assert len(units) == 2

    def test_extract_all_german_months(self, rag_agent):
        """Teste explizit alle deutschen Monate."""
        month_names = ["Januar", "Februar", "März", "April", "Mai", "Juni",
                       "Juli", "August", "September", "Oktober", "November", "Dezember"]

        for month_name in month_names:
            units, months = rag_agent._extract_helper(f"Bericht für {month_name}")
            assert month_name.lower() in months, f"{month_name} sollte erkannt werden"

    def test_extract_business_unit_abbreviation(self, rag_agent):
        """Testet ob 'bus' für 'beide business units' funktioniert."""
        units, months = rag_agent._extract_helper("beide bus")
        assert len(units) == 2
        assert "hometech" in units
        assert "digital_solutions" in units


class TestFlatten:
    """Tests für die flatten() Hilfsfunktion."""

    @pytest.fixture
    def mock_vector_store(self):
        return Mock()

    @pytest.fixture
    def mock_plot_function(self):
        return Mock()

    @pytest.fixture
    def rag_agent(self, mock_vector_store, mock_plot_function):
        return RAGAgent(vector_store=mock_vector_store, api_key="test-key", plot_function=mock_plot_function)

    def test_flatten_nested_list(self, rag_agent):
        """Flacht verschachtelte Listen ab."""
        nested = [[1, 2], [3, [4, 5]], 6]
        result = rag_agent.flatten(nested)
        assert result == [1, 2, 3, 4, 5, 6]

    def test_flatten_already_flat(self, rag_agent):
        """Bereits flache Liste bleibt unverändert."""
        flat = [1, 2, 3, 4]
        result = rag_agent.flatten(flat)
        assert result == [1, 2, 3, 4]

    def test_flatten_empty_list(self, rag_agent):
        """Leere Liste bleibt leer."""
        result = rag_agent.flatten([])
        assert result == []

    def test_flatten_deeply_nested(self, rag_agent):
        """Tief verschachtelte Listen."""
        deeply_nested = [[[[[1]]]]]
        result = rag_agent.flatten(deeply_nested)
        assert result == [1]


class TestExtractPlotDataFromAnswer:
    """Tests für die Plot-Daten-Extraktion."""

    @pytest.fixture
    def mock_vector_store(self):
        mock = Mock()
        mock.query_vector_db.return_value = {
            'documents': [['Test content']],
            'metadatas': [[{'source': 'test', 'heading': 'Test', 'month': 'Januar', 'type': 'test'}]]
        }
        return mock

    @pytest.fixture
    def mock_plot_function(self):
        return Mock()

    @pytest.fixture
    def rag_agent(self, mock_vector_store, mock_plot_function):
        return RAGAgent(vector_store=mock_vector_store, api_key="test-key", plot_function=mock_plot_function)

    @patch('anthropic.Anthropic')
    def test_extract_plot_data_valid_json(self, mock_anthropic_class, rag_agent):
        """Extrahiert gültige Plot-Daten."""
        # Mock Claude Response mit gültigem JSON
        mock_client = MagicMock()
        mock_response = MagicMock()
        valid_json = {
            "labels": {"x": "Monat", "y": "Umsatz"},
            "values": {"Home Tech": {"Januar": 100000}},
            "units": ["Home Tech"],
            "title": "Test"
        }
        mock_response.content = [MagicMock(text=json.dumps(valid_json))]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic_class.return_value = mock_client
        rag_agent.client = mock_client

        # Initialisiere result Dictionary
        rag_agent.result = {'question': 'Test', 'context': 'Test'}

        result = rag_agent._extract_plot_data_from_answer("Test query", "Test answer")

        assert result is not None
        assert "labels" in result
        assert "values" in result
        assert "units" in result

    @patch('anthropic.Anthropic')
    def test_extract_plot_data_missing_labels_x(self, mock_anthropic_class, rag_agent):
        """Validierung schlägt fehl bei fehlenden labels.x."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        invalid_json = {
            "labels": {"y": "Umsatz"},  # x fehlt
            "values": {"Home Tech": {"Januar": 100000}},
            "units": ["Home Tech"]
        }
        mock_response.content = [MagicMock(text=json.dumps(invalid_json))]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic_class.return_value = mock_client
        rag_agent.client = mock_client

        rag_agent.result = {'question': 'Test', 'context': 'Test'}

        result = rag_agent._extract_plot_data_from_answer("Test query", "Test answer")
        assert result is None

    @patch('anthropic.Anthropic')
    def test_extract_plot_data_invalid_units(self, mock_anthropic_class, rag_agent):
        """Validierung schlägt fehl bei ungültigen Units."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        invalid_json = {
            "labels": {"x": "Monat", "y": "Umsatz"},
            "values": {"Invalid Unit": {"Januar": 100000}},
            "units": ["Invalid Unit"]  # Nicht in valid_units
        }
        mock_response.content = [MagicMock(text=json.dumps(invalid_json))]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic_class.return_value = mock_client
        rag_agent.client = mock_client

        rag_agent.result = {'question': 'Test', 'context': 'Test'}

        result = rag_agent._extract_plot_data_from_answer("Test query", "Test answer")
        assert result is None

    @patch('anthropic.Anthropic')
    def test_extract_plot_data_empty_values(self, mock_anthropic_class, rag_agent):
        """Validierung schlägt fehl bei leeren values."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        invalid_json = {
            "labels": {"x": "Monat", "y": "Umsatz"},
            "values": {},  # Leer
            "units": ["Home Tech"]
        }
        mock_response.content = [MagicMock(text=json.dumps(invalid_json))]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic_class.return_value = mock_client
        rag_agent.client = mock_client

        rag_agent.result = {'question': 'Test', 'context': 'Test'}

        result = rag_agent._extract_plot_data_from_answer("Test query", "Test answer")
        assert result is None

    @patch('anthropic.Anthropic')
    def test_extract_plot_data_json_decode_error(self, mock_anthropic_class, rag_agent):
        """Behandelt JSON Parse-Fehler."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Invalid JSON {{{")]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic_class.return_value = mock_client
        rag_agent.client = mock_client

        rag_agent.result = {'question': 'Test', 'context': 'Test'}

        result = rag_agent._extract_plot_data_from_answer("Test query", "Test answer")
        assert result is None

    @patch('anthropic.Anthropic')
    def test_extract_plot_data_missing_title_adds_empty(self, mock_anthropic_class, rag_agent):
        """Fügt leeren Titel hinzu wenn nicht vorhanden."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        json_without_title = {
            "labels": {"x": "Monat", "y": "Umsatz"},
            "values": {"Home Tech": {"Januar": 100000}},
            "units": ["Home Tech"]
            # title fehlt
        }
        mock_response.content = [MagicMock(text=json.dumps(json_without_title))]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic_class.return_value = mock_client
        rag_agent.client = mock_client

        rag_agent.result = {'question': 'Test', 'context': 'Test'}

        result = rag_agent._extract_plot_data_from_answer("Test query", "Test answer")
        assert result is not None
        assert result['title'] == ""


class TestQueryWithPlotCreation:
    """Tests für Plot-Erstellung in query() Methode."""

    @pytest.fixture
    def mock_vector_store(self):
        mock = Mock()
        mock.query_vector_db.return_value = {
            'documents': [['Umsätze im Januar: 100000 Euro']],
            'metadatas': [[{'source': 'test', 'heading': 'Januar 2023', 'month': 'Januar', 'type': 'test'}]]
        }
        return mock

    @pytest.fixture
    def mock_plot_function(self):
        """Mock Plot-Funktion die erfolgreich ist."""
        mock = Mock()
        mock.return_value = "plot_result_success"
        return mock

    @pytest.fixture
    def rag_agent(self, mock_vector_store, mock_plot_function):
        return RAGAgent(vector_store=mock_vector_store, api_key="test-key", plot_function=mock_plot_function)

    @patch('anthropic.Anthropic')
    def test_query_with_successful_plot_creation(self, mock_anthropic_class, rag_agent, mock_plot_function):
        """Plot wird erfolgreich erstellt."""
        mock_client = MagicMock()

        # Erste Response: Normale Antwort
        first_response = MagicMock()
        first_response.content = [MagicMock(text="Die Umsätze betrugen 100000 Euro")]

        # Zweite Response: Plot-Daten-Extraktion
        second_response = MagicMock()
        plot_json = {
            "labels": {"x": "Monat", "y": "Umsatz"},
            "values": {"Home Tech": {"Januar": 100000}},
            "units": ["Home Tech"],
            "title": "Umsätze"
        }
        second_response.content = [MagicMock(text=json.dumps(plot_json))]

        # Dritte Response: Erfolgs-Nachricht
        third_response = MagicMock()
        third_response.content = [MagicMock(text="Die Grafik wurde erstellt!")]

        mock_client.messages.create.side_effect = [first_response, second_response, third_response]
        mock_anthropic_class.return_value = mock_client
        rag_agent.client = mock_client

        result = rag_agent.query("Plotte die Umsätze", n_results=1)

        assert isinstance(result, dict)
        assert result['plot_created'] is True
        assert result['plot_result'] == "plot_result_success"
        assert "Grafik wurde erstellt" in result['answer']
        mock_plot_function.assert_called_once()

    @patch('anthropic.Anthropic')
    def test_query_with_failed_plot_creation(self, mock_anthropic_class, rag_agent):
        """Plot-Erstellung schlägt fehl."""
        # Überschreibe plot_function um Fehler zu werfen
        rag_agent.plot_function = Mock(side_effect=Exception("Plot error"))

        mock_client = MagicMock()

        first_response = MagicMock()
        first_response.content = [MagicMock(text="Die Umsätze betrugen 100000 Euro")]

        second_response = MagicMock()
        plot_json = {
            "labels": {"x": "Monat", "y": "Umsatz"},
            "values": {"Home Tech": {"Januar": 100000}},
            "units": ["Home Tech"],
            "title": "Umsätze"
        }
        second_response.content = [MagicMock(text=json.dumps(plot_json))]

        # Error-Response
        error_response = MagicMock()
        error_response.content = [MagicMock(text="Die Visualisierung war nicht möglich.")]

        mock_client.messages.create.side_effect = [first_response, second_response, error_response]
        mock_anthropic_class.return_value = mock_client
        rag_agent.client = mock_client

        result = rag_agent.query("Plotte die Umsätze", n_results=1)

        assert isinstance(result, dict)
        assert result['plot_created'] is False
        assert "Visualisierung war nicht möglich" in result['answer']

    @patch('anthropic.Anthropic')
    def test_query_with_no_plot_data_extracted(self, mock_anthropic_class, rag_agent):
        """Keine Plot-Daten konnten extrahiert werden."""
        mock_client = MagicMock()

        first_response = MagicMock()
        first_response.content = [MagicMock(text="Keine Daten verfügbar")]

        # Zweite Response: Ungültiges JSON
        second_response = MagicMock()
        second_response.content = [MagicMock(text="Invalid JSON")]

        # No-Data Response
        no_data_response = MagicMock()
        no_data_response.content = [MagicMock(text="Keine numerischen Daten verfügbar.")]

        mock_client.messages.create.side_effect = [first_response, second_response, no_data_response]
        mock_anthropic_class.return_value = mock_client
        rag_agent.client = mock_client

        result = rag_agent.query("Plotte die Umsätze", n_results=1)

        assert isinstance(result, dict)
        assert result['plot_created'] is False
        assert "Keine numerischen Daten" in result['answer']


class TestQuellenPhrasing:
    """Tests für _quellen_phrasing() Methode."""

    @pytest.fixture
    def mock_vector_store(self):
        return Mock()

    @pytest.fixture
    def mock_plot_function(self):
        return Mock()

    @pytest.fixture
    def rag_agent(self, mock_vector_store, mock_plot_function):
        return RAGAgent(vector_store=mock_vector_store, api_key="test-key", plot_function=mock_plot_function)

    def test_quellen_phrasing_basic(self, rag_agent):
        """Grundlegende Quellen-Extraktion."""
        context = """[Dokument 1]
Quelle: test
Überschrift: Januar 2023
Monat: Januar
Typ: Bericht
Inhalt: Test content
============================================================"""

        result = rag_agent._quellen_phrasing("Frage zu Januar", context)

        assert isinstance(result, list)
        assert len(result) > 0
        # Letztes Element ist die User-Anfrage
        last_item = result[-1]
        assert "erwähnte Monate" in last_item
        assert "Angefragte Business Units" in last_item