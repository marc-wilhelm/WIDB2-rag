# Schritt 3: Embedding & Vektordatenbank

from typing import List, Dict, Optional
import chromadb
from chromadb.utils import embedding_functions
import config


class VectorStoreManager:
    """
    Verwaltet die Erstellung von Embeddings und die Speicherung
    der unstrukturierten Textdaten in einer Chroma Vektordatenbank.
    """

    def __init__(
        self,
        db_path: str = config.CHROMA_DB_PATH,
        collection_name: str = config.CHROMA_COLLECTION_NAME
    ):
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

    def ingest_markdown_data(self, markdown_data: List[Dict[str, str]]) -> None:
        """
        Erzeugt Embeddings und speichert Chunks + Metadaten in Chroma.
        """
        if not markdown_data:
            print("Keine Markdown-Daten zum Verarbeiten vorhanden.")
            return

        documents: List[str] = []
        metadatas: List[Dict] = []
        ids: List[str] = []

        for paragraph in markdown_data:
            if not paragraph.get("text") or not paragraph["text"].strip():
                continue

            enriched_text = (
                f"Business Unit: {paragraph['source']}\n"
                f"Typ: {paragraph['type']}\n"
                f"Monat: {paragraph['month']}\n\n"
                f"{paragraph['text']}"
            )

            documents.append(enriched_text)

            metadatas.append({
                "source": paragraph["source"],        # hometech | digital_solutions
                "heading": paragraph["heading"],
                "month": paragraph["month"] or "",
                "type": paragraph["type"]             # monatsbericht | einleitung | fazit
            })

            ids.append(f"{paragraph['source']}_para_{paragraph['paragraph_id']}")

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

    def query_vector_db(
        self,
        query_text: str,
        n_results: int = 5,
        where: Optional[Dict] = None
    ) -> Dict:
        """
        Hybride Suche:
        - Semantische Suche über Embeddings
        - Optionale Keyword-/Metadatenfilter (month, source, type)
        """
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where=where,
                include=["metadatas", "documents", "distances"]
            )
            return results
        except Exception as e:
            print(f"Fehler bei der Vektor-Suche: {e}")
            return {}
