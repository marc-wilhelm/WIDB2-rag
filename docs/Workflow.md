# Workflow
## 1. Datenaufbereitung und Dokumentenvorbereitung
### 1.1 Umwandlung der Quelldokumente

- PDF-Dateien werden zunächst in Markdown-Dateien (.md) konvertiert.

- Jedem Dokument wird manuell ein zusätzlicher Abschnitt „Fazit“ hinzugefügt, um eine einheitliche inhaltliche Zusammenfassung sicherzustellen und die spätere Retrieval-Qualität zu erhöhen.

###1.2 Ergänzende Wissensquellen (TBD)

- Dies beinhaltet die Integration einer FAQ-Datei mit vordefinierten, häufig gestellten Fragen und zugehörigen Antworten.

- Diese FAQ soll ebenfalls als Markdown-Datei vorliegen und beim Systemstart eingelesen werden, um wiederkehrende Anfragen effizient abzudecken.

## 2. Textbereinigung und Strukturierung
### 2.1 Bereinigung und Extraktion des Rohtextes

- Die Markdown-Dateien werden bereinigt, um irrelevante Formatierungen, Artefakte oder redundante Inhalte zu entfernen.

- Ziel ist die Extraktion eines sauberen, semantisch konsistenten Rohtextes.

###2.2 Segmentierung nach inhaltlichen Einheiten

- Der bereinigte Text wird anhand von Überschriften und Abschnitten in kleinere, in sich geschlossene Textsegmente aufgeteilt.

- Diese Segmentierung dient der späteren granularen Suche und verbessert die Relevanz der Retrieval-Ergebnisse.

2.3 Anreicherung mit Metadaten

- Jeder Textabschnitt wird mit Metainformationen versehen, z. B.:

	- Monat oder Zeitbezug

	- Quelle bzw. Ursprungsdokument

	- Eindeutige Abschnitts- oder Dokumenten-IDs

- Diese Metadaten ermöglichen gezieltes Filtern und kontextsensitives Retrieval.

## 3. Vektorisierung und Datenhaltung
### 3.1 Embedding der Textdaten

- Die unstrukturierten Textsegmente werden gemeinsam mit ihren Metadaten und IDs mittels eines Embedding-Modells in Vektoren überführt.

- Eingesetztes Modell:

	-  ``` paraphrase-multilingual-MiniLM-L12-v2 ```

- Dieses Modell erlaubt eine mehrsprachige semantische Repräsentation der Inhalte.

### 3.2 Speicherung in der Vektordatenbank

- Die erzeugten Vektoren werden in der ChromaDB gespeichert.

- ChromaDB dient als performante Vektordatenbank für semantische Ähnlichkeitssuchen im RAG-System.

##4. KI-Modell und Systemkonfiguration
###4.1 Sprachmodell / KI-Agent

- Eingesetzte KI-Version:

	- Claude Sonnet 4: ``` claude-sonnet-4-20250514```

- Das Modell übernimmt die eigentliche Antwortgenerierung auf Basis der bereitgestellten Kontextinformationen.

### 4.2 System-Prompt und Regeln

- Ein zentraler System-Prompt definiert verbindliche Regeln für den Umgang mit Quellen, z. B.:

	- Nutzung ausschließlich der bereitgestellten Inhalte

	- Korrekte Referenzierung bzw. Zusammenfassung

	- Vermeidung von Halluzinationen

## 5. Retrieval-Augmented Generation (RAG)
### 5.1 Verbindung von Datenbank und Sprachmodell

- Das RAG-System verbindet die ChromaDB-Vektordatenbank mit dem Claude-LLM.

- Auf Basis einer Benutzeranfrage werden semantisch relevante Textsegmente aus der Datenbank abgerufen.

### 5.2 Kontextübergabe an das Sprachmodell

- Die gefilterten Textabschnitte werden gemeinsam mit der ursprünglichen Benutzeranfrage an das LLM übergeben.

- Dabei gelten feste Einschränkungen:

	- Maximale Anzahl der übergebenen Textsegmente (Absätze)

	- Maximale Antwortlänge in Tokens

Diese Begrenzungen dienen der Kostenkontrolle, Antwortqualität und Systemstabilität.

## 6. Frontend und Benutzerinteraktion

- Das Frontend besteht aus einer mit Streamlit umgesetzten Webanwendung.

- Die Anwendung dient als Benutzeroberfläche zur Eingabe von Anfragen und zur Darstellung der KI-generierten Antworten.

(Zugriff und konkrete Schnittstellen können hier noch spezifiziert werden.)

## 7. Grafikerstelung (TBD)

- Falls eine Benutzeranfrage explizit die Erstellung einer Grafik oder Visualisierung verlangt:

	- Greift die KI auf ein separates Modul zu.

	- Dieses Modul wird mit anfragerelevanten Daten parametrisiert und erzeugt die gewünschte Grafik.
