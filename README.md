# RAG-Projekt



TODO: EINLEITUNG EINFÜGEN

## Inhaltverzeichnis

- [Einrichten](#einrichten)
- [Projekt Struktur](#projekt-struktur)

## Einrichten

### Voraussetzungen

- Python 3.12.x ([Download](https://www.python.org/downloads/release/python-31212/))

### Python Installation

Erst wird eine virtuelle Python umgebung benötigt. Mit dem folgenden Befehl wird das .venv erstellt, aktiviert und Packages installiert:

**POWERSHELL**
```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt
```

**BASH**
```bash
python -m venv .venv && source .venv/Scripts/activate && pip install -r requirements.txt
```

Für mehr Hilfe siehe [Setup Doku](docs/Setup.md)

## Projekt Struktur

```
WIDB2-rag/
│
├── data/                           # Daten-Verzeichnis
│
├── docs/                           # Dokumentation
│
├── src/                            # Hauptcode
│   └── tests/                      # Tests
│
├── streamlit/                      # Frontend
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
  <tr><td>Niclas Gencer</td>     <td></td></tr>
  <tr><td>Paul Gütling</td>      <td></td></tr>
  <tr><td>Johanna Kießling</td>  <td>6622009</td></tr>
  <tr><td>Maike Knauer</td>      <td>6622007</td></tr>
  <tr><td>Marc Wilhelm</td>      <td>6622005</td></tr>
</table>