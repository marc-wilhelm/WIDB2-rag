<div align="center">

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.52.1-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-1.3.7-orange?style=flat)
![Claude](https://img.shields.io/badge/Claude_API-0.75.0-CC785C?style=flat&logo=anthropic&logoColor=white)

---

## **RAG-Chatbot für BWA**

### Prototypische Implementierung eines dokumenten-basierten Chatbots

Entwicklung eines RAG-basierten Chatbots, mit dem Controller natürlich-sprachige Fragen zu DATEV-BWA Berichten stellen können. Das System liefert ausschließlich dokumenten-basierte Antworten und vermeidet Halluzinationen durch strikte Bindung an die vorliegenden Geschäftsdokumente.

---
</div>

## Inhaltverzeichnis

- [Einrichten](#einrichten)
  - [Python Installation](#python-installation)
  - [Virtuelle Python Umgebung](#virtuelle-python-umgebung)
  - [.env Datei erstellen](#env-datei-erstellen)
  - [Streamlit](#streamlit)
- [Projekt Struktur](#projekt-struktur)
- [Team](#team)

## Einrichten

### Python Installation

Bitte installiere eine Python Version. Für beste kompatibilität empfehlen wir Python 3.12.X [[Download](https://www.python.org/downloads/release/python-31212/)].

### Virtuelle Python Umgebung

Erst wird eine virtuelle Python umgebung benötigt. Mit dem folgenden Befehl wird das .venv erstellt, aktiviert und Packages installiert:

**POWERSHELL**
```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt
```

**BASH**
```bash
python -m venv .venv && source .venv/Scripts/activate && pip install -r requirements.txt
```

### .env Datei erstellen

Damit der Chatbot funktional ist, bitte erstelle eine `.env` datei, in der, der entsprechende API Key eingetragen wird. Zu Orientierung der Syntax siehe das `.env.
example`.

Für mehr Hilfe siehe [Setup Doku](docs/Setup.md)

### Streamlit

Um das Frontend des Chatbots zu starten, führe folgenden Befehl im Projekt-Root-Verzeichnis aus:

**BASH**
```bash
streamlit run streamlit/Home.py
```

## Projekt Struktur

```
WIDB2-rag/
│
├── data/                           # Daten-Verzeichnis
│   └── chroma_db/                 
│
├── docs/                           # Dokumentation
│
├── src/                            # Hauptcode
│   └── tests/
│
├── streamlit/                      # Frontend-Ordner
│   └── pages/                      # Unterseiten
│
├── .env.example                   # Environment-Template
├── .gitignore
├── requirements.txt
└── README.md
```

## Team

Hinter diesem Projekt im Modul WIDB2 stehen:

<table>
    <tr><th>Name</th>              <th>Matrikelnummer</th></tr>
    <tr><td>Paul Gütling</td>      <td>5621177</td></tr>
    <tr><td>Marc Wilhelm</td>      <td>6622005</td></tr>
    <tr><td>Niclas Gencer</td>     <td>6622006</td></tr>
    <tr><td>Maike Knauer</td>      <td>6622007</td></tr>
    <tr><td>Johanna Kießling</td>  <td>6622009</td></tr>
</table>
