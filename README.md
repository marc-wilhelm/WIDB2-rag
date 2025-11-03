# RAG-Projekt

TODO: EINLEITUNG EINFÜGEN

## Inhaltverzeichnis

- [Einrichten](#einrichten)
- [Projekt Struktur](#projekt-struktur)
- [Weitere Punkte](#weitere-punkte)

## Einrichten

TODO: EINRICHTUNG BESCHREIBEN

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
├── app/                            # Frontend
│   ├── components/                 # UI-Komponenten
│   └── styles/                     # Custom CSS
│
├── tests/                          # Tests
│
├── scripts/                       # Setup & Utility Scripts
│
├── .env.example                   # Environment-Template
├── .env                           # Tatsächliche Secrets (in .gitignore!)
├── .gitignore
├── .dockerignore
├── docker-compose.yml
├── Dockerfile                     # Falls separate Dockerfile gewünscht
├── requirements.txt
└── README.md
```

## Weitere Punkte
