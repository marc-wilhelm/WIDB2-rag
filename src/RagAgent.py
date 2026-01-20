from typing import List, Dict, Optional, Callable, Any
import anthropic
import json
import re
from VectoreStoreManager import VectorStoreManager
from Grafikplotter import grafik_plotten_dynamisch
import config


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

    
    def _quellen_phrasing(self,user_question,context):
        """
        Hauptmethode: Zur besseren Kontextualisierung der Quellen für das RAG Modell.

        Args:
            user_question: Die Frage des Benutzers
            context: Der in einem String gejoined Context

        Returns:
            Liste mit Dictionaries, die Relevante Informationen und Filter wiederspiegeln.
        """
        
        
        lst = []
        temp = []
        
        context = context.replace("{","").replace("}", "") #.replace("'","").replace('"',"")
        context = context.split("=")
        context = list(filter(None,context))
        for text in context: 
            text = text.split("]")
            text = list(filter(None,text))
            for word in text:
                word = word.split("\n")
                word = list(filter(None,word))
            
            
                lst.append(word)
        
        
        lst = self.flatten(lst)    
        
        
        for i in sorted([i for i, x in enumerate(lst) if "[Dokument " in x], reverse=True):
            lst.pop(i)
            temp.append(lst[i:])
            lst = lst[:i]
        
            
        lst = sorted(temp, reverse=True)
        temp = []
        

        for i in lst:
            Zitier_Dict = {"Quelle": None, "Überschrift": None, "Monat": None, "Typ": None, "Business Unit": None, "Inhalt": None}
            
            Zitier_Dict["Inhalt"] = lst[lst.index(i)][-1].capitalize()
            print(lst[lst.index(i)][-1].capitalize())
            for x in list(Zitier_Dict.keys()):
                for y in i:
                    if str(x)+":" in y:
                        if Zitier_Dict[x] == None:
                            Zitier_Dict[x] = (y.split(":")[1]).strip().capitalize()
                        if Zitier_Dict[x] == '':
                            Zitier_Dict[x] == "NA"
            
            for key in list(Zitier_Dict.keys()):
                if Zitier_Dict.get(key) in ('',None):
                    del Zitier_Dict[key]
                            
            temp.append(Zitier_Dict)
        
                    
        lst = temp 
        temp = []
        

        units, months = self._extract_helper(user_question)
        Nutzer_Anfrage = {"Angefragte Business Units" : units, "erwähnte Monate" : months}
        
        
        lst.append(Nutzer_Anfrage)
    
    
        return  lst              
    
        
    def flatten(self,lst):
        result = []
        for item in lst:
            if isinstance(item, list):          
                result.extend(self.flatten(item))
            else:
                result.append(item)              
        return result

    
    
    def query(self, user_question: str,
              n_results: int = config.RAG_N_RESULTS,
              max_tokens: int = config.CLAUDE_MAX_TOKENS,
              model: str = config.CLAUDE_MODEL,
              mode: str = "single",
              chat_history: Optional[List[Dict]] = None,
              ) -> str:
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


        #SPOTLIGHT: Neuer Prompt Abschnitt der versucht der KI weiter die Regeln zur Quellenangabe nahezubringen
        #Ich glaube es hilft, aber ich bin auch sau müde
        user_prompt_parts.append(f"""\n\nFür die Quellen und die Zitierung gibt es zuletzt nocheinmal eine kleine Vergleichsbasis, um die Genauigkeit 
                                 und Relevanz dieser zu prüfen.\n Mit dieser Liste von Dictionaries {self._quellen_phrasing(user_question,context)} 
                                 \nKannst du Anhand von angrefragten Zeiträumen, sowie Metadaten und die Wiedergabe welche Quelle(n), deren Titel etc. angegeben werden sollen
                                 prüfen. Schreibe hierbei die **Quellen** die du ausgibst Lisitenartig auf. Zähle also von eins [1] beginnend hoch. 
                                 \n Die Quellen werden wie Folgt ausgegeben: [1] Dictionary["Quelle"]: "quelle", Dictionary["überschrift"]: "überschrift"
                                 \n Das letzte dict in der Liste ist IMMER Herausgezogene Monats und Unit Daten, die zur Orientierung bei der Quellensuche helfen.""")
        
        user_prompt = "\n\n".join(user_prompt_parts)


        # 4. Initialisiere Ergebnis-Dictionary
        self.result = {
            'answer': '',
            'question': user_question,
            'plot_created': False,
            'plot_result': None,
            'plot_data': None,
            'context': context,   
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
            self.result['answer'] = answer

            # 7. Prüfe ob Plot benötigt wird
            should_plot = self._should_create_plot(user_question)
            
            if should_plot:
                print("🎨 Plot-Anfrage erkannt, extrahiere Daten...")
                
                # Daten extrahieren
                plot_data = self._extract_plot_data_from_answer(user_prompt, answer)
                
                if plot_data:
                    print(f"✓ Daten extrahiert: {list(plot_data.keys())}")
                    self.result['plot_data'] = plot_data
                    
                    # Plot erstellen
                    try:
                        plot_result = self.plot_function(**plot_data, animate=False)
                        self.result['plot_created'] = True
                        self.result['plot_result'] = plot_result
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
                        self.result['answer'] = desc_message.content[0].text
                        
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
                        self.result['answer'] = error_message.content[0].text
                        
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
                    self.result['answer'] = no_data_message.content[0].text
                    
             #SPOTLIGHT: Beim Plotten kommt immer erstmal eine Wall of Text 
             #bevor die Grafik erscheint - muss noch getestet werden, ob jetzt weg        
            return self.result
        
        except Exception as e:
            error_msg = f"Fehler bei der Claude API: {e}"
            print(f"\n{error_msg}")
            self.result['answer'] = error_msg
            return self.result

    def _should_create_plot(self, query: str) -> bool:
        """Prüft ob die Anfrage eine Visualisierung benötigt."""
        plot_keywords = [
            'plot', 'plotte', 'diagramm', 'graph', 'visualisier',
            'zeige', 'chart', 'grafik', 'darstell', 'verlauf',
            'entwicklung', 'trend', 'zeichne'
        ]
        return any(keyword in query.lower() for keyword in plot_keywords)

    #SPOTLIGHT: Alte funktion umgeschrieben.
    def _extract_helper(self,*query: str) -> List[str]:
            # --- Hilfskonstanten ---
            GERMAN_MONTHS = ["januar", "februar", "märz", "april", "mai", "juni", "juli", "august", "september", "oktober", "november", "dezember"]
            BUSINESS_UNIT_KEYWORDS = {
            "hometech": ["home tech", "hometech", "home-tech"],
            "digital_solutions": ["digital solutions", "digital solution", "digital business", "digital_solutions"]
        }
            
            units,months = [], []
            
            for segments in query:
                
                segments = segments.lower()
                
                
                unitt = [unit for unit, keywords in BUSINESS_UNIT_KEYWORDS.items() if any(k in segments for k in keywords)]
                if not unitt and re.search(r"\b(beide|alle)\s+(business units|bus|business unit)\b", segments):
                    unitt = list(BUSINESS_UNIT_KEYWORDS.keys())
                units.extend(unitt)    
            
                monthh = [month for month in GERMAN_MONTHS if month in segments]
                if not monthh and re.search(r"\b(alle|entwicklung)\s+(quartal|zeitraum|monat)\b", segments):
                    monthh = list(GERMAN_MONTHS)
                months.extend(monthh)
                
                
            units = list(set(units))
            months = list(set(months))
            print(units)
            print(months)
            
            return units,months
    


    def _extract_plot_data_from_answer(self, query: str, answer: str) -> Optional[Dict]:
        """
        Nutzt Claude um strukturierte Plot-Daten zu extrahieren.
        Passt die Daten an grafik_plotten_dynamisch an.
        """
        # Kontext aus den Dokumenten
        self.result["context"] = self.create_context_prompt(query, n_results=5)
        units, months = self._extract_helper(self.result["context"],answer,self.result["question"])
        
        extraction_prompt = f"""
Erstelle aus der folgenden ANTWORT ein JSON-Objekt für einen Plotter.
Nutze den KONTEXT nur, um fehlende numerische Werte präzise zu ergänzen.

### STRIKTE REGELN FÜR DIE STRUKTUR:
1. **LABELS:** Muss ein Dictionary mit den Keys "x" und "y" sein!
   Beispiel: "labels": {{"x": "Monat", "y": "Umsatz in EUR"}}
2. **VALUES:** - Bei einer Datenreihe: Ein Dictionary mit {{"Monat": Wert}}.
   - Bei mehreren Reihen (z.B. Units): Ein Dictionary, das pro Unit ein Unter-Dictionary mit {{"Monat": Wert}} enthält.
3. **REINE ZAHLEN:** Nur Integer oder Float (z.B. 305200). Keine Punkte, keine Währungssymbole.
4. **FORMAT:** Gib NUR das reine JSON zurück.

### BEISPIEL-STRUKTUR (ZIELFORMAT):
{{
  "labels": {{"x": "Zeitraum", "y": "Betrag in Euro"}},
  "values": {{
    "Digital Solutions": {{"Januar": 305200, "Februar": 289450, "März": 316800, "April": 274900}},
    "Home Tech": {{"Januar": 222606, "Februar": 212215, "März": 223515, "April": 210658}}
  }},
  "units": ["Digital Solutions", "Home Tech"],
  "title": "Umsatzvergleich Jan-Apr"
}}

ANTWORT:
{answer}

DOKUMENTE:
{self.result['context']}

gefragte
UNITS:
{units}

gefragte
MONATE:
{months}


Gib ausschließlich das JSON zurück, ohne zusätzlichen Text oder Markdown.
"""
        print(extraction_prompt)
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