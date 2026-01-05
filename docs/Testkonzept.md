# Testkonzept

## Teststrategie

Das RAG-Projekt umfasst 586 Zeilen produktiven Code im src-Verzeichnis. Die Teststrategie konzentriert sich auf das korrekte Zusammenspiel der Systemkomponenten, da der Hauptwert in der Integration von Markdown-Verarbeitung, Vektordatenbank und RAG-Pipeline liegt.

Ein vollständiges Test-Pyramid-Modell mit 70% Unit Tests wäre unverhältnismäßig, da die meiste Logik API-Orchestrierung und Datentransformation zwischen externen Services betrifft. Zur Erklärung des Test-Pyramid-Modells empfehlen wir den Blog-Beitrag von CircleCI [*'The testing pyramid: Strategic software testing for Agile teams'*](https://circleci.com/blog/testing-pyramid/). Stattdessen wurde ein ausgewogener Mix aus Unit Tests für isolierbare Funktionen und Integration Tests für die Systemkomponenten gewählt.

### Testarten

- **Unit Tests:** Regex-Pattern-Matching und Markdown-Parsing
- **Integration Tests:** Zusammenspiel von MarkdownCleaner, VectorStoreManager und RAG-Pipeline
- **Manuelle Tests:** UI-Tests in Streamlit und End-to-End-Szenarien mit echter Claude API

Die Unit Tests decken die String-Verarbeitungslogik im MarkdownCleaner ab. Dazu gehört die Extraktion von Monatsinformationen mittels regulärer Ausdrücke und das Parsing der Markdown-Struktur.

Die Integration Tests validieren die vollständige Pipeline vom Markdown-Dokument über die Bereinigung und das Embedding bis zur Speicherung in ChromaDB und dem Retrieval. ChromaDB wird mit echten temporären Instanzen getestet, während die Claude API gemockt wird um Kosten zu vermeiden.

Nicht getestet werden die externe Claude API selbst, das Streamlit-Frontend sowie die Script-Dateien für die Initialisierung, da diese keine testbare Business-Logik enthalten.

## Testergebnisse

Die Test-Suite umfasst 687 Zeilen Testcode in 4 Dateien. Alle 32 Tests laufen erfolgreich durch.

<div align="center">

```
================================ test session starts =================================
collected 32 items

src/tests/unit/test_markdown_cleaner.py ................            [ 50%]
src/tests/unit/test_rag_agent.py .....                              [ 65%]
src/tests/integration/test_integration_vector_store.py .......      [ 87%]
src/tests/integration/test_integration_rag_pipeline.py ......       [100%]

================================ 32 passed in 28.92s =================================
```

</div>

### Coverage-Bericht

<div align="center">

```
Name                                    Stmts   Miss  Cover
-------------------------------------------------------------
src/MarkdownCleaner.py                     63      0   100%
src/RagAgent.py                            33      0   100%
src/VectoreStoreManager.py                 42      7    83%
src/config.py                              23      0   100%
src/init_db.py                             41     41     0%
src/init_interactive.py                    53     53     0%
-------------------------------------------------------------
TOTAL                                     653    109    83%
```

</div>

### Interpretation

Die Kernmodule erreichen eine sehr gute Coverage. MarkdownCleaner und RagAgent sind vollständig abgedeckt, VectorStoreManager liegt bei 83%. Die fehlenden 17% betreffen hauptsächlich Error-Handling-Pfade die in der Praxis schwer zu testen sind.

Die Script-Dateien haben erwartungsgemäß 0% Coverage, da sie reine Orchestrierungslogik ohne testbare Business-Logik enthalten.

Die Gesamtcoverage von 83% ist für ein RAG-Projekt dieser Größenordnung sehr gut. Bei API-lastigen Systemen ist eine Coverage von 80-85% realistisch und ausreichend.


## Test-Ausführung

```bash
# Alle Tests mit Coverage-Report
pytest src/tests/ -v --cov=src

# Nur Unit Tests
pytest src/tests/unit/ -v

# Nur Integration Tests
pytest src/tests/integration/ -v
```

## Test-Struktur

```
src/
├── tests/
│   ├── unit/
│   │   ├── test_markdown_cleaner.py
│   │   └── test_rag_agent.py
│   └── integration/
│       ├── test_integration_vector_store.py
│       └── test_integration_rag_pipeline.py
```

## Mocking-Strategie

Die externe Claude API wird konsequent gemockt um keine Kosten zu verursachen und reproduzierbare Tests zu ermöglichen. ChromaDB läuft mit echten temporären Instanzen da dies die reale Integration besser testet als Mocks.

## Qualitative Tests für LLM-Antworten

Die automatisierten Tests prüfen funktionale Aspekte wie Datenfluss und Systemintegration. Bei RAG-Systemen ist jedoch die inhaltliche Qualität der generierten 
Antworten entscheidend, denn ein funktional korrektes aber inhaltlich unzuverlässiges System ist für Anwender wertlos. Daher werden qualitative Tests manuell 
durchgeführt. Die Tests basieren auf vordefinierten Fragen unterschiedlicher Komplexität. Die LLM-Antworten werden mit den tatsächlichen Berichten abgeglichen. Bei unzureichenden Antworten wird die Konfiguration überprüft: System Prompt, Chunk-Größe, Retrieval-Parameter und Context-Zusammenstellung.

[Hier](Fragen-Katalog.md) ist der Fragen-Katalog ersichtlich.