# Wichtige Docker Commands für dein RAG-Projekt

## Setup (einmalig)
```bash
# 1. Image bauen (installiert alle Packages aus requirements.txt)
docker-compose build

# 2. Container starten
docker-compose up -d
```

## Entwicklung (täglich)
```bash
# Container starten (falls gestoppt)
docker-compose up -d

# Logs anschauen (um Fehler zu sehen)
docker-compose logs -f

# In den Container "reingehen" (für Python-Shell oder Tests)
docker exec -it rag-app bash

# Im Container dann z.B.:
python src/app.py
# oder
streamlit run src/app.py
```

## Bei Änderungen
```bash
# Neue Packages in requirements.txt hinzugefügt?
docker-compose build          # Image neu bauen
docker-compose up -d          # Container neu starten

# Nur Code geändert (kein requirements.txt)?
# Nichts tun - Code wird automatisch synchronisiert durch volumes!
```

## Aufräumen
```bash
# Container stoppen
docker-compose down

# Container stoppen UND Image löschen (für kompletten Neustart)
docker-compose down --rmi all

# Alle ungenutzten Images/Container/Volumes löschen (Vorsicht!)
docker system prune -a --volumes
```

## Debugging
```bash
# Status aller Container sehen
docker ps -a

# Logs eines bestimmten Containers
docker logs rag-app

# In laufenden Container reinschauen
docker exec -it rag-app bash

# Im Container Python-Shell starten
docker exec -it rag-app python
```

## PyCharm Integration
```bash
# Container muss laufen für PyCharm Remote Interpreter
docker-compose up -d

# In PyCharm:
# Settings → Project → Python Interpreter
# → Add Interpreter → Docker Compose
# → Service: rag-app
```

## Streamlit starten
```bash
# Im Container (docker exec -it rag-app bash):
streamlit run src/app.py

# Dann im Browser öffnen: http://localhost:8501
```

## Schnellreferenz
```bash
docker-compose build      # Neu bauen
docker-compose up -d      # Starten (detached)
docker-compose down       # Stoppen
docker-compose logs -f    # Logs live anzeigen
docker exec -it rag-app bash  # In Container gehen
```

## Troubleshooting
```bash
# Port schon belegt?
docker-compose down
netstat -ano | findstr :8501  # Windows
# oder
lsof -i :8501  # Mac/Linux

# Container startet nicht?
docker-compose logs rag-app

# Alles zurücksetzen?
docker-compose down --rmi all --volumes
docker-compose build
docker-compose up -d
```