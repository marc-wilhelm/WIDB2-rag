# Schritt 3: Embedding & Vektordatenbank

from typing import List, Dict
import chromadb
from chromadb.utils import embedding_functions
import config


class VectorStoreManager:
    """
    Verwaltet die Erstellung von Embeddings und die Speicherung
    der unstrukturierten Textdaten in einer Chroma Vektordatenbank.
    """

    def __init__(self, db_path: str = config.CHROMA_DB_PATH, collection_name: str = config.CHROMA_COLLECTION_NAME):
        self.embedding_model_name = config.EMBEDDING_MODEL

        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=self.embedding_model_name
        )

        self.client = chromadb.PersistentClient(path=db_path)

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_function
        )

        print(f"ChromaDB initialisiert. Path: {db_path}")
        print(f"Collection '{collection_name}' geladen/erstellt.")
        print(f"Verwendetes Embedding-Modell: {self.embedding_model_name}")

    def ingest_markdown_data(self, markdown_data: List[Dict[str, str]]):
        if not markdown_data:
            print("Keine Markdown-Daten zum Verarbeiten vorhanden.")
            return

        documents = []
        metadatas = []
        ids = []

        for paragraph in markdown_data:
            if not paragraph['text'] or not paragraph['text'].strip():
                continue

            documents.append(paragraph['text'])

            month_value = paragraph['month'] if paragraph['month'] is not None else ""

            metadatas.append({
                'source': 'markdown',
                'heading': paragraph['heading'],
                'month': month_value,
                'type': paragraph['type']
            })

            ids.append(f"md_para_{paragraph['paragraph_id']}")

        if not documents:
            print("Keine gültigen Text-Dokumente zum Speichern gefunden.")
            return

        try:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            print(f"Erfolgreich {len(documents)} Text-Abschnitte in Chroma geladen.")
        except Exception as e:
            print(f"Fehler beim Laden der Daten in Chroma: {e}")

    def query_vector_db(self, query_text: str, n_results: int = 2) -> Dict:
        """
        Führt eine stille Ähnlichkeitssuche durch (ohne Debug-Ausgaben).
        """
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results,
                include=['metadatas', 'documents', 'distances']
            )
            return results
        except Exception as e:
            print(f"Fehler bei der Vektor-Suche: {e}")
            return {}