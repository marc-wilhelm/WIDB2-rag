# Streamlit Frontend

## Projektstruktur

Das Frontend wird im Ordner `streamlit` verwaltet und ist modular in mehrere Seiten aufgeteilt:

- **Home.py** - Startseite mit einer Einführung und Übersicht über den Chatbot
- **Chat.py** - Hauptfunktionalität: Die Chat-Schnittstelle für Benutzeranfragen an das RAG-System
- **Info.py** - Informationsseite mit Details zur technischen Architektur und Funktionsweise des Chatbots

## Voraussetzungen

Bevor das Frontend gestartet werden kann, muss eine Vektordatenbank initialisiert werden. Diese wird mit folgendem Befehl erstellt:
```bash
python src/init_db.py
```

**Hinweis:** Stelle sicher, dass das Setup erfolgreich eingerichtet ist ([Link zum Einrichten](../README.md#einrichten)).

## Lokale Ausführung

Um das Streamlit-Frontend lokal zu starten, führe folgenden Befehl im Terminal aus:
```bash
python -m streamlit run streamlit/Home.py
```

Nach der Ausführung öffnet sich automatisch ein Browser-Tab mit der Anwendung. Alternativ ist das Frontend auch manuell unter folgender Adresse erreichbar:
```
http://localhost:8501/
```

Die Anwendung kann jederzeit im Terminal mit `STRG + C` beendet werden.