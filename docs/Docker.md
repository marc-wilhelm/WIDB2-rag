# Docker Workflow

## Docker-Compose Commands

```bash
# Container stoppen und entfernen (inkl. verwaiste Container)
docker-compose down --remove-orphans

# Image(s) neu bauen basierend auf Dockerfile
docker-compose build

# Container im Hintergrund starten (-d = detached mode)
docker-compose up -d
```

## Image vs. Container

- **Image**: Unveränderbare Vorlage (Blueprint) mit OS, Dependencies, Code
- **Container**: Laufende Instanz eines Images (wie ein Prozess)

**Analogie**: Image = Kuchenrezept, Container = gebackener Kuchen

## Docker Workflow im Projekt

### 1. Dockerfile
- Definiert **wie** ein Image gebaut wird
- Enthält Anweisungen: Basis-Image, Dependencies installieren, Code kopieren
- Wird für **widb2-rag** Service verwendet

### 2. docker-compose.yml
- Orchestriert **mehrere Services** zusammen
- Definiert Netzwerke, Volumes, Umgebungsvariablen
- Vereinfacht Multi-Container-Setup

## Services im Projekt

| Service | Typ | Beschreibung |
|---------|-----|--------------|
| **widb2-rag** | ✅ Build | Wird aus lokalem Dockerfile gebaut |
| **python-env** | 📦 Image | Nutzt bereits gebautes `widb2-rag:latest` Image |
| **weaviate** | 📦 Image | Externes Image (Vektordatenbank) |
| **text2vec-model2vec** | 📦 Image | Externes Image (Embedding-Modell) |

### Build vs. Image
- **Build** (`widb2-rag`): Dockerfile wird ausgeführt → Image erstellt → Container gestartet
- **Image** (andere Services): Fertiges Image wird gepullt → Container gestartet

## Typischer Workflow

1. Code-Änderung → `docker-compose build` → Image neu bauen
2. `docker-compose up -d` → Container aus Images starten
3. `docker-compose down --remove-orphans` → Aufräumen

**Hinweis**: `python-env` und `widb2-rag` nutzen dasselbe Image, aber unterschiedliche `command` und Volumes.