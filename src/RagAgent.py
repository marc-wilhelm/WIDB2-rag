# Schritt 4: RAG-Agent mit Claude API

from typing import List, Dict
import anthropic
from VectoreStoreManager import VectorStoreManager
import config

class RAGAgent:
    """
    Der RAG-Agent verbindet die Vektordatenbank mit der Claude API.
    Er nimmt Benutzerfragen entgegen, sucht relevante Dokumente
    und generiert präzise Antworten basierend auf dem Kontext.
    """

    def __init__(self, vector_store: VectorStoreManager, api_key: str):
        """
        Initialisiert den RAG-Agent.

        Args:
            vector_store: Eine Instanz des VectorStoreManager
            api_key: Dein Anthropic API-Schlüssel
        """
        self.vector_store = vector_store
        self.client = anthropic.Anthropic(api_key=api_key)
        print("RAG-Agent erfolgreich initialisiert.")

    def create_context_prompt(self, query: str, n_results: int = 5) -> str:
        """
        Erstellt den Kontext-Prompt für Claude.

        1. Sucht relevante Dokumente in der Vektordatenbank
        2. Formatiert sie für Claude

        Args:
            query: Die Benutzerfrage
            n_results: Anzahl der abzurufenden Dokumente

        Returns:
            Formatierter Kontext-String
        """
        # 1. Relevante Dokumente aus der Vektordatenbank abrufen
        results = self.vector_store.query_vector_db(query, n_results=n_results)

        # 2. Kontext formatieren
        context_parts = []

        if results and 'documents' in results and results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                meta = results['metadatas'][0][i]

                # Formatiere jedes Dokument mit seinen Metadaten
                context_parts.append(
                    f"[Dokument {i + 1}]\n"
                    f"Quelle: {meta.get('source', 'N/A')}\n"
                    f"Überschrift: {meta.get('heading', 'N/A')}\n"
                    f"Monat: {meta.get('month', 'N/A')}\n"
                    f"Typ: {meta.get('type', 'N/A')}\n"
                    f"Inhalt:\n{doc}\n"
                    f"{'=' * 60}\n"
                )

        if not context_parts:
            return "Keine relevanten Dokumente gefunden."

        return "\n".join(context_parts)

    def query(self, user_question: str,
          n_results: int = config.RAG_N_RESULTS,
          max_tokens: int = config.CLAUDE_MAX_TOKENS,
          model: str = config.CLAUDE_MODEL) -> str:
        """
        Hauptmethode: Beantwortet eine Benutzerfrage mit RAG.

        Args:
            user_question: Die Frage des Benutzers
            n_results: Anzahl der Dokumente für den Kontext
            max_tokens: Maximale Länge der Antwort

        Returns:
            Die generierte Antwort von Claude
        """

        # 1. Kontext aus der Vektordatenbank erstellen => alle Chunks nutzen
        context = self.create_context_prompt(user_question, n_results)

        # 2. System-Prompt definieren (gibt Claude Anweisungen)
        system_prompt = config.SYSTEM_PROMPT

        # 3. User-Prompt erstellen (kombiniert Kontext + Frage)
        user_prompt = f"""Hier sind die relevanten Dokumente:

        {context}

        Benutzerfrage: {user_question}

        Bitte beantworte die Frage basierend auf den obigen Dokumenten."""

        # 4. Claude API aufrufen
        try:
            message = self.client.messages.create(
                model=model,  # Aktuelles Sonnet-Modell
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )

            # 5. Antwort extrahieren
            answer = message.content[0].text

            print(answer)
            print("=" * 70)

            return answer

        except Exception as e:
            error_msg = f"Fehler bei der Claude API: {e}"
            print(f"\n{error_msg}")
            return error_msg