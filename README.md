# RAG-Projekt



TODO: EINLEITUNG EINFÜGEN

## Inhaltverzeichnis

- [Einrichten](#einrichten)
- [Projekt Struktur](#projekt-struktur)

## Einrichten

### Voraussetzungen

- Python 3.12.x ([Download](https://www.python.org/downloads/release/python-31212/))
- Docker Desktop ([Installationsanleitung](https://docs.docker.com/get-started/introduction/get-docker-desktop/))

### Python Installation

Python wird **nur** für die Verwaltung des Docker-Environments benötigt (z.B. IDE-Integration, Tools). Der Code wird ausschließlich im Docker-Container ausgeführt.

**Empfohlen**: Python 3.12.x

### Docker Desktop Installation

Docker stellt sicher, dass alle Teammitglieder unter identischen Bedingungen arbeiten:
- Einheitliche Python-Version
- Identische Package-Versionen
- Einfaches Setup ohne manuelle Konfiguration

**Weitere Infos**: [Docker Workflow im Projekt](docs/Docker.md)

## Projekt Struktur

```
WIDB2-rag/
│
├── data/                           # Daten-Verzeichnis
│   ├── raw/                        # Original-Dateien
│   ├── processed/                  # Verarbeitete/Gechunkte Daten
│   └── vector_db/                  # Vektordatenbank
│
├── docs/                           # Dokumentation
│
├── src/                            # Hauptcode
│   │
│   ├── data_processing/            # Datenverarbeitung
│   │
│   ├── rag/                        # RAG-Kernlogik
│   │
│   ├── llm/                        # LLM-Integration
│   │
│   └── utils/                      # Hilfsfunktionen
│
├── streamlit/                      # Frontend
│   └── pages/                      # Unterseiten
│
├── tests/                          # Tests
│
├── .env.example                   # Environment-Template
├── .env                           # Tatsächliche Secrets (in .gitignore)
├── .gitignore
├── .dockerignore
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## Team

Hinter diesem Projekt im Modul WIDB2 stehen:

<table>
  <tr><th>Name</th>              <th>Matrikelnummer</th></tr>
  <tr><td>Niclas Gencer</td>     <td></td></tr>
  <tr><td>Paul Gütling</td>      <td></td></tr>
  <tr><td>Johanna Kießling</td>  <td>6622009</td></tr>
  <tr><td>Maike Knauer</td>      <td>6622007</td></tr>
  <tr><td>Marc Wilhelm</td>      <td>6622005</td></tr>
</table>