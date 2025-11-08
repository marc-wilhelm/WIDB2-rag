# Vektorendatenbanken

## Schlüsselfunktionen

### Vektorielle Speicherung
  - Datenpunkte werden durch Embeddingmodelle in Vektoren mit fester Anzahl von Dimensionen dargestellt

  - Jede Dimension eines Vektors ist ein latentes Merkmal (=nicht direkt beobachtabares Merkmal, sondern wird durch mathematische Algorithmen abgeleitet)

  - Auch Metadaten (Titel, Beschreibung, Datentyp) werden pro Vektor gespeichert


### Vektorindizierung
 - mittels ML-Algorithmen werden Vektoren indiziert um Suchfunktionen zu beschleunigen 

 Möglichkeiten zu Indizierung:
 - HNSW (Hierarchical Navigable Small World)
   Hierarchische Struktur:
   Obere Schichten: Verbindung zwischen Vektoren weit auseinander => ermöglichen schnel in grobe Regionen des Vektorraums zu navigieren
   Untere Schichten: Vektoren sind enger verbunden was genauere Suche ermöglicht tatsächich den nächsten Nachbarn zu finden 
   => Guter Kompromiss aus Geschwindigkeit & Genauigkeit v.a. bei großem Mengen von Vektordaten 

 - LSH
 - PQ


### Ähnlichkteitssuche basierend auf Abfragen
  - Abfragevektor wird vom gleichen Embeddingmodell wie beim Embedding der Dokomente erstellt 

  - i.d.R. mehrere Algorithmen um Approximate Neares Neigbour (ANN) zu finden => Abstände zwischen Abfrage und in Datenbank gespeicherte Vektoren werden berechneet
  =>  semantische Suche 

- Es gibt verschiedene Möglichkeiten zu Ähnlichkeitsmessung zwischen 2 Vektoren z.B. Konsinusähnlichkeit (misst die Winkel zwischen 2 Vekoren ) und euklidischer Distanz (misst den Abstand)


  - Möglichkeit hybride Suche:
    Kombination aus semantischer Vektorsuche und fuzzy Keyword-Suche mit OpenSearch => wird nicht von allen Vektordatenbanken unterstützt


## Möglichkeiten zur Verwaltung von Vektoren als Anwendung in einem RAG-System

### Vektordatenbanken
Speicherung, Verwaltung und Abfrage von Vektordaten => ermöglicht schnelle Suche in großen Mengen von Vektordaten

Beispiele:
Open-Sorce Lösungen wie Weaviate,  Milvus (für extrem große Datenmengen geeignet), Chroma die integrierte
RESTfulAPIs und Unterstützung für Python bieten
Cloud-datenbanken wie Pinecone (nicht Open-Source, unterstützt keine hybride Suche)

#### Chroma 
= In-Memory-Datenbank, Daten werden hauptsächlich im Arbeitsspeicher gehalten => besonders schnelle Zugriffszeiten
Speicherarchitektur kann auch auf persistente Speicherung erweitert werden, um Daten über Neustarts hinaus zu erhalten, indem Daten bei Beenden gespeichert werden 
Indexierungsalgorithmen wie Approximate-Nearest-Neighbor (ANN) werden verwendert 
Bitete einfache API mit 4 Haupfunktionen => gilt als Benutzer freundlicher als z.B. Pinecone
=> gleiche API die auch in Python-Notebooks verwendet wir
Unterstützung für LangChain (Pytohn & JavaScript) und LlamaIndex
Umfassenden Dokumentation & Tutorials 
Unterstützt verschiedene Embeddingmodelle (Standardeinstellung: all-MiniLM-L6-v2 )
- unterstützt hybride Suche
- eignet sich nicht für sehr große Datenmenge (niedrigere Skalierbarkeit)
- läuft komplett in-process innerhab eines Python-Scripts => keine externe Datenbank nötig
- besonders für kleine, schnelle Projekte geeignet

#### Weaviate
läuft als einzelnes Binary im Docker-Container oder als Cluster in Kubernets => Implementierung aufwändiger als bei Chroma
erzeugt wahlweise selbst Embeddings oder nutzt externe Modelle
Semantische und realtionale Abfragen lassen sich elegant kombinieren
=> unterstützt strukturierte und unstrukturierte Daten sehr gut
unterstützt hybride Query
Schnittstelle für Python


### Vektor-Suchbibliotheken (Vektorindexbibliotheken)
Verwendung vor allem vor dem Aufkommen von Vektordatenbanken => mit ihrer Hilfe können schnell leistungsstarke Prottoypen eines Vektorsuchsystems erstellt werden 
 z.B. FAISS (Open-Source), ermöglicht keine hypbride Suche , Azure Cognitive search


### Vektor-Suchplugins
Erweitern Funktionalititä von bestehenden Datenbanksystemen, indem sie Möglichkeit hinzufügen innerhalb dieser Systeme Vektorsuchen durchzuführen
=> Erweiterung bestehender Architekturen (oftmals eingeschränkt)
Beispiele:
PostgreSQL mit pgvector, Elasticsearch 


=> Empfehlung: Für Entwicklung schnell zu erstellender Prototypen Vektor-Suchbibliothek wie FAISS
Bei RAG-Anwendungen mit großen Datenmengen und hohen Anforderungen an Performance & Ergebnisqualität Vektordatenbank nutzen (z.B. Chroma )


## Hybride Datenbankarchitektur
Zwei Seperate Datenbanken:
Vektordatenbank (z.B. Chroma) für unstrukturierten Text-Daten aus PDF
SQL-Datenbank (z.B. MySQL) für sturkturierten Excel-Daten
=> Verknüpfung der Daten über gemeinsamte ID wie Monat

SQL-Datenbak wird angesprochen indem LLM Datenbankabfrage in SQL aus Nutzeranfrage generiert (Dieser Schritt kann herausfordernd sein)

## Fazit Datenbankwahl
am besten geeignet: Chroma oder Weaviate
beide OpenSource => kostenlose Variante
beide sehr gute Python API
unterstützen beide hybride Suche (semantsich und Stichwortbasiert)
Chroma: sehr einfache Implementierung, läuft nur in Python Script nach Pip-Installation => keine seperate Dantenbank-oder Serverinstallation notwendig
Weaviate: erofrdert seperate Installation läuft in Docker-Container oder auf eigenem Server (sehr aufwändig), komplexer als Chroma
Datenbankserver über RESTful API/ Python-Client erreichbar
Beide können mit Langchain und LlamaIndex verbunden werden, wobei Chroma einfacher ist das es direkt in Python integriert werden kann und keine externe API benötigt
ABER: Weaviate unterstützt parallel auch sehr gut Verarbeitung strukturierter Daten



## Anbindung von Datenbanken an RAG
OpenSource Bibliotheken wie LangChain oder LlamaIndex können LLm mit Vektordatenbank inkl. Embeddingmodell und Dokumenten-Importer verbinden

## Verbesserungsmöglichkeiten: 

### Rerank
Vektordatenbank liefert im Retrievalprozess bei der Suche meist mehrere Treffer die standardmäßig nicht nach Relevanz geordnet sind
Beim Reranking werden Suchergebnisse in einer zusätzlichen Vorabanfrage bewertet (in Verbindung mit LLM)
Nur am höchsten bewertete Chunk wird in eigentlicher RAG-Abfrage verwendet 


## Beispiel Workflow für RAG-system mit Weaviate
https://colab.research.google.com/github/geosword/devclub-weaviate/blob/main/weaviate.ipynb#scrollTo=qzv7IMBJHSBh

Aufbau Workflow:

1. Benötigte Bibliotheken installieren / importieren (openai, weaviate-cline, langchain, pypdf)

2. GPT4 über OpenAI-API aufrufen
   - API-Key angeben
   - Nachrichtenformat aufbauen
   - Chunks ggf. an Prompt anhängen
   - Modell-Antwort-Textfeld zurückgeben

3. Erstellen einer neuen Weaviate Collection (entspricht Tabelle in Datenbank)
enthält Felder wie content (eigentlicher Chunk-Text), Metadaten (z.B. Seitenzahl, Chunknummer...)
Embedding-Modelll definieren (hier modell von openAI)

4. PDF laden und in Chunks aufteilen
Gesamtes PDF wird geladen und in Chunks (inkl. Überschneidungen) zerlegt
Pro Chunk wird Datensatz (bestehend aus Text und zugehörigen Metadaten in Weaviate eingefügt)

5. Funktion für Semantische Suche von zur Anfrage ähnlichen Texten in der Weaviate-Collection

6. in den ersten Schritten angelegte Funktionen werden alle innerhalb des eigentlichen RAG-Prozesses nacheinander aufgerufen 


### Notwendige Anpassungen für eigenes Projekt
Idee: Ein Datensatz / objekt in einer Collection kann neben Content-Feld (enthält Text für jeweiligen Monat aus PDF => wird vektorisiert), noch weitere Felder wie Monat, Umsatz, Personalkosten... haben (=> strukturierte Daten)
Die strukturierten Daten können auch als Filter eingesetzt werden 
Weaviate kombiniert dann die semantische Suche mit klassichem Filtern 







## Quellen:
https://www.ibm.com/de-de/think/topics/vector-database
https://www.iese.fraunhofer.de/blog/retrieval-augmented-generation-rag/
https://latenode.com/de/blog/ai-frameworks-technical-infrastructure/rag-retrieval-augmented-generation/rag-system-tutorial-build-retrieval-augmented-generation-from-scratch
https://www.astera.com/de/type/blog/building-a-knowledge-base-rag/
https://www.x1f.one/blogbeitrag/welche-architektur-hinter-sicheren-und-verlaesslichen-rag-systemen-steckt/
https://www.chitika.com/rag-sql-database-integration/
https://www.econstor.eu/bitstream/10419/285313/1/Reinking-Becker-Large-Language-Modelle.pdf
https://www.ionos.de/digitalguide/server/knowhow/chroma-db/
https://meetcody.ai/de/blog/die-5-besten-vektordatenbanken-fuer-2024/
https://ai-rockstars.de/vektor-datenbanken/#Fazit_Welche_Vektor-DB_passt_fuer_welchen_Zweck
https://medium.com/aingineer/a-complete-guide-to-implementing-hybrid-rag-86c0febba474



## Weitere Beispiele Weaviate für RAG-System nutzen
https://docs.weaviate.io/weaviate/starter-guides/generative
https://bratanic-tomaz.medium.com/how-to-implement-weaviate-rag-applications-with-local-llms-and-embedding-models-24a9128eaf84
https://colab.research.google.com/github/geosword/devclub-weaviate/blob/main/weaviate.ipynb





  