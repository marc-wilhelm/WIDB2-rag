# Workflow

## Datenaufbereitung

**Markdown**

- Aus der Markdown Datei wird der Text extrahiert und nach ##-Abästzen strukturiert
    - zusätzlich Meta-Infos zum Absatz hinzufügen (Monat, Quelle)

**Excel**

- Umwandlung der Daten von einem Wide-Format zu einem Long-Format (für RDBMS)
   - NaN-Werte werden entfernt
   - Sicherstellen der Datentypen

## Datenspeicherung & -verwaltung

### Strukturierte Daten

- Excel wird in SQLLite abgespeichert (für größere Datenmengen lieber PostgreSQL nehmen)

### Unstruktirierte Daten

- Mittels eines Embedding Modells unstrukrierte Daten (Text) in die Vektoredatenbank (CromaDB, Weaviate) überführen
  - speichert auch die Meta-Daten und IDs
