from typing import List, Dict, Optional, Callable, Any
import anthropic
from VectoreStoreManager import VectorStoreManager
import config
from Grafikplotter import grafik_plotten_dynamisch
import json
import re


class RAGAgent:
    """
    Der RAG-Agent verbindet die Vektordatenbank mit der Claude API.
    Er nimmt Benutzerfragen entgegen, sucht relevante Dokumente
    und generiert präzise Antworten basierend auf dem Kontext.
    """

    def __init__(self, vector_store: VectorStoreManager, api_key: str, plot_function: Callable):
        """
        Initialisiert den RAG-Agent.

        Args:
            vector_store: Eine Instanz des VectorStoreManager
            api_key: Dein Anthropic API-Schlüssel
            plot_function: Funktion zum Erstellen von Plots
        """
        self.vector_store = vector_store
        self.client = anthropic.Anthropic(api_key=api_key)
        self.plot_function = plot_function
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

    def format_chat_history(self, chat_history: List[Dict]) -> str:
        """
        Formatiert die Chat-History für den Prompt.

        Args:
            chat_history: Liste von Nachrichten mit 'role' und 'content'

        Returns:
            Formatierter Chat-Verlauf als String
        """
        if not chat_history:
            return ""

        history_parts = ["Bisheriger Chat-Verlauf:"]

        for msg in chat_history:
            role = "Benutzer" if msg['role'] == 'user' else "Assistent"
            history_parts.append(f"[{role}]: {msg['content']}")

        history_parts.append("\n--- Ende des Chat-Verlaufs ---\n")

        return "\n".join(history_parts)

    def query(self, user_question: str,
              n_results: int = config.RAG_N_RESULTS,
              max_tokens: int = config.CLAUDE_MAX_TOKENS,
              model: str = config.CLAUDE_MODEL,
              mode: str = "single",
              chat_history: Optional[List[Dict]] = None,
              **kwargs) -> Dict[str, Any]:
        """
        Hauptmethode: Beantwortet eine Benutzerfrage mit RAG.

        Args:
            user_question: Die Frage des Benutzers
            n_results: Anzahl der Dokumente für den Kontext
            max_tokens: Maximale Länge der Antwort
            model: Claude-Modell
            mode: "single" (ohne Chat-History) oder "multi" (mit Chat-History)
            chat_history: Optional - Liste der bisherigen Nachrichten für Kontext
            **kwargs: Weitere Parameter für rag_agent.query()

        Returns:
            Dictionary mit 'answer', 'plot_created', 'plot_result', 'plot_data'
        """

        # 1. Kontext aus der Vektordatenbank erstellen
        context = self.create_context_prompt(user_question, n_results)

        # 2. System-Prompt definieren
        system_prompt = config.SYSTEM_PROMPT

        # 3. User-Prompt erstellen
        user_prompt_parts = []

        # Chat-History hinzufügen nur im "multi" Modus
        if mode == "multi" and chat_history:
            history_text = self.format_chat_history(chat_history)
            user_prompt_parts.append(history_text)

        # Dokumente hinzufügen
        user_prompt_parts.append(f"Hier sind die relevanten Dokumente:\n\n{context}")

        # Aktuelle Frage hinzufügen
        if mode == "multi":
            user_prompt_parts.append(f"\nAktuelle Benutzerfrage: {user_question}")
            user_prompt_parts.append("\nBitte beantworte die aktuelle Frage basierend auf den obigen Dokumenten und dem Chat-Verlauf.")
        else:
            user_prompt_parts.append(f"\nBenutzerfrage: {user_question}")
            user_prompt_parts.append("\nBitte beantworte die Frage basierend auf den obigen Dokumenten.")

        user_prompt = "\n\n".join(user_prompt_parts)

        # 4. Initialisiere Ergebnis-Dictionary
        result = {
            'answer': '',
            'plot_created': False,
            'plot_result': None,
            'plot_data': None
        }

        try:
            # 5. Claude API aufrufen
            message = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )

            # 6. Antwort extrahieren
            answer = message.content[0].text
            result['answer'] = answer

            # 7. Prüfe ob Plot benötigt wird
            should_plot = self._should_create_plot(user_question)
            
            if should_plot:
                print("🎨 Plot-Anfrage erkannt, extrahiere Daten...")
                
                # Daten extrahieren
                plot_data = self._extract_plot_data_from_answer(user_prompt, answer)
                
                if plot_data:
                    print(f"✓ Daten extrahiert: {list(plot_data.keys())}")
                    result['plot_data'] = plot_data
                    
                    # Plot erstellen
                    try:
                        plot_result = self.plot_function(**plot_data, animate=False)
                        result['plot_created'] = True
                        result['plot_result'] = plot_result
                        print("✓ Plot erfolgreich erstellt!")
                        
                        # Semantische Antwort von Claude generieren
                        title = plot_data.get('title', 'die Daten')
                        units_str = ', '.join(plot_data['units'])
                        
                        success_prompt = f"""Die Grafik wurde erfolgreich erstellt!

Ursprüngliche Anfrage: {user_question}
Grafik-Titel: {title}
Dargestellte Einheiten: {units_str}

Schreibe eine kurze, freundliche Antwort (2-3 Sätze), die:
1. Bestätigt, dass die Grafik erstellt wurde
2. Kurz erwähnt, was visualisiert wird
3. Einladend ist für weitere Fragen

Sei prägnant und natürlich."""

                        desc_message = self.client.messages.create(
                            model=model,
                            max_tokens=150,
                            messages=[{"role": "user", "content": success_prompt}]
                        )
                        result['answer'] = desc_message.content[0].text
                        
                    except Exception as e:
                        print(f"⚠ Fehler beim Plot erstellen: {e}")
                        print(f"   Übergebene Daten: {plot_data}")
                        
                        # Semantische Fehler-Antwort von Claude
                        error_prompt = f"""Die Grafik konnte leider nicht erstellt werden.

Ursprüngliche Anfrage: {user_question}
Fehler: {str(e)}

Schreibe eine kurze, hilfreiche Antwort (2-3 Sätze), die:
1. Erklärt, dass die Visualisierung nicht möglich war
2. Einen möglichen Grund nennt (z.B. unvollständige Daten)
3. Anbietet, die Daten textuell zu präsentieren oder anders zu helfen

Sei freundlich und lösungsorientiert."""

                        error_message = self.client.messages.create(
                            model=model,
                            max_tokens=150,
                            messages=[{"role": "user", "content": error_prompt}]
                        )
                        result['answer'] = error_message.content[0].text
                        
                else:
                    print("⚠ Keine numerischen Daten für Plot gefunden")
                    
                    # Semantische Antwort für fehlende Daten
                    no_data_prompt = f"""Für die Anfrage konnten keine geeigneten Daten für eine Visualisierung gefunden werden.

Ursprüngliche Anfrage: {user_question}

Schreibe eine kurze, hilfreiche Antwort (2-3 Sätze), die:
1. Erklärt, dass keine numerischen Daten verfügbar sind
2. Anbietet, die verfügbaren Informationen textuell darzustellen
3. Fragt, ob eine andere Darstellung gewünscht wird

Sei freundlich und hilfsbereit."""

                    no_data_message = self.client.messages.create(
                        model=model,
                        max_tokens=150,
                        messages=[{"role": "user", "content": no_data_prompt}]
                    )
                    result['answer'] = no_data_message.content[0].text
            
            return result
        
        except Exception as e:
            error_msg = f"Fehler bei der Claude API: {e}"
            print(f"\n{error_msg}")
            result['answer'] = error_msg
            return result

    def _should_create_plot(self, query: str) -> bool:
        """Prüft ob die Anfrage eine Visualisierung benötigt."""
        plot_keywords = [
            'plot', 'plotte', 'diagramm', 'graph', 'visualisier',
            'zeige', 'chart', 'grafik', 'darstell', 'verlauf',
            'entwicklung', 'trend', 'vergleich'
        ]
        return any(keyword in query.lower() for keyword in plot_keywords)

    def _extract_plot_data_from_answer(self, query: str, answer: str) -> Optional[Dict]:
        """
        Nutzt Claude um strukturierte Plot-Daten zu extrahieren.
        Passt die Daten an grafik_plotten_dynamisch an.
        """
        # Kontext aus den Dokumenten
        context = self.create_context_prompt(query, n_results=5)
        
        extraction_prompt = f"""
Basierend auf folgender Antwort und den Originaldokumenten, extrahiere Daten für einen Plot.

ANTWORT:
{answer}

DOKUMENTE:
{context}

WICHTIG: Die Funktion erwartet folgendes Format:

{{
    "labels": {{
        "x": "Beschreibung X-Achse (z.B. 'Monat', 'Datum')",
        "y": "Beschreibung Y-Achse (z.B. 'Umsatz in €', 'Anzahl')"
    }},
    "values": {{
        "UnitName1": {{"2024-01-01": 100, "2024-02-01": 150}},
        "UnitName2": {{"2024-01-01": 80, "2024-02-01": 120}}
    }},
    "units": ["UnitName1", "UnitName2"],
    "title": "Passender Titel für den Plot"
}}

REGELN:
1. "units" muss entweder ["Home Tech"] oder ["Digital Solutions"] oder beide enthalten
2. Wenn nur eine Unit: values kann auch unverschachtelt sein: {{"2024-01-01": 100, ...}}
3. X-Werte sollten Datumsstrings im ISO-Format sein (YYYY-MM-DD) oder lesbare Strings
4. Y-Werte müssen numerisch sein (int oder float)
5. Falls keine numerischen Daten vorhanden: gib {{}} zurück

Extrahiere NUR aus den gegebenen Dokumenten. Erfinde keine Daten.
Gib ausschließlich das JSON zurück, ohne zusätzlichen Text oder Markdown.
"""
        
        try:
            message = self.client.messages.create(
                model=config.CLAUDE_MODEL,
                max_tokens=2000,
                messages=[{"role": "user", "content": extraction_prompt}]
            )
            
            response_text = message.content[0].text.strip()
            
            # Debug-Ausgabe
            print(f"📋 Claude's Rohantwort (erste 200 Zeichen):\n{response_text[:200]}...")
            
            # Entferne Markdown-Formatierung
            response_text = re.sub(r'```json?\s*', '', response_text)
            response_text = re.sub(r'```\s*$', '', response_text)
            response_text = response_text.strip()
            
            # Parse JSON
            plot_data = json.loads(response_text)
            
            # Validierung
            if not plot_data:
                return None
            
            # Prüfe ob alle erforderlichen Felder vorhanden sind
            required_fields = ['labels', 'values', 'units']
            if not all(field in plot_data for field in required_fields):
                print(f"⚠ Fehlende Felder in plot_data: {[f for f in required_fields if f not in plot_data]}")
                return None
            
            # Validiere labels
            if 'x' not in plot_data['labels'] or 'y' not in plot_data['labels']:
                print("⚠ labels muss 'x' und 'y' enthalten")
                return None
            
            # Validiere units
            valid_units = {"Home Tech", "Digital Solutions"}
            if not set(plot_data['units']).issubset(valid_units):
                print(f"⚠ Ungültige units: {plot_data['units']}")
                return None
            
            # Validiere dass Daten vorhanden sind
            if not plot_data['values']:
                print("⚠ Keine Werte in 'values'")
                return None
            
            # Optional: title kann fehlen
            if 'title' not in plot_data:
                plot_data['title'] = ""
            
            return plot_data
            
        except json.JSONDecodeError as e:
            print(f"⚠ JSON Parse-Fehler: {e}")
            print(f"   Erhaltener Text: {response_text[:500] if 'response_text' in locals() else 'N/A'}")
            return None
        except Exception as e:
            print(f"⚠ Fehler bei Datenextraktion: {e}")
            return None