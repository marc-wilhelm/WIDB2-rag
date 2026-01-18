from typing import List, Dict, Optional, Callable, Any
import anthropic
import json
import re

from VectoreStoreManager import VectorStoreManager
from Grafikplotter import grafik_plotten_dynamisch
import config

# --- Hilfskonstanten ---
GERMAN_MONTHS = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]
BUSINESS_UNIT_KEYWORDS = {
    "hometech": ["home tech", "hometech", "home-tech"],
    "digital_solutions": ["digital solutions", "digital solution", "digital business", "digital_solutions"]
}

def extract_business_units_from_query(query: str) -> List[str]:
    q = query.lower()
    units = [unit for unit, keywords in BUSINESS_UNIT_KEYWORDS.items() if any(k in q for k in keywords)]
    if not units and re.search(r"\b(beide|alle)\s+(business units|bus|business unit)\b", q):
        units = list(BUSINESS_UNIT_KEYWORDS.keys())
    return units

class RAGAgent:
    def __init__(self, vector_store: VectorStoreManager, api_key: str, plot_function: Callable = grafik_plotten_dynamisch):
        self.vector_store = vector_store
        self.client = anthropic.Anthropic(api_key=api_key)
        self.plot_function = plot_function
        print("RAG-Agent erfolgreich initialisiert.")

    def create_context_prompt(self, query: str, n_results: int = 12) -> str:
        """
        Erstellt einen Kontext-String mit strikter Nummerierung für korrekte Zitierung.
        """
        extracted_months = [m for m in GERMAN_MONTHS if m.lower() in query.lower()]
        extracted_units = extract_business_units_from_query(query)
        
        # Falls "alle Monate" gefragt sind, Filter aufheben
        if re.search(r"\b(alle monate|über alle monate)\b", query.lower()): 
            extracted_months = []

        results = self.vector_store.query_vector_db(query_text=query, n_results=n_results)
        if not results or not results.get("documents"): 
            return "Keine Dokumente in der Datenbank gefunden."

        docs = [d for l in results["documents"] for d in l]
        metas = [m for l in results["metadatas"] for m in l]
        
        # Ranking-Logik (Fazit-Chunks nach oben)
        sorted_indices = sorted(
            range(len(docs)), 
            key=lambda i: (0 if "faz" in metas[i].get("heading", "").lower() else 1)
        )[:10] # Wir nehmen bis zu 10 relevante Chunks

        context_parts = []
        # STRIKTE NUMMERIERUNG: Diese IDs [1], [2]... muss Claude im Text verwenden
        for idx, i in enumerate(sorted_indices, start=1):
            m = metas[i]
            source_id = m.get('source', 'BWA_Dokument')
            month = m.get('month', 'Unbekannter Monat')
            heading = m.get('heading', 'Allgemein')
            
            context_parts.append(
                f"--- REFERENZ-ID: [{idx}] ---\n"
                f"QUELLE: {source_id}\n"
                f"MONAT/ZEITRAUM: {month}\n"
                f"BEREICH: {heading}\n"
                f"INHALT:\n{docs[i]}\n"
                f"--- ENDE REFERENZ [{idx}] ---\n"
            )
            
        return "\n".join(context_parts)

    def format_chat_history(self, chat_history: List[Dict]) -> str:
        if not chat_history: return ""
        history_parts = ["Bisheriger Chat-Verlauf:"]
        for msg in chat_history:
            role = "Benutzer" if msg["role"] == "user" else "Assistent"
            history_parts.append(f"[{role}]: {msg['content']}")
        return "\n".join(history_parts) + "\n--- Ende Chat-Verlauf ---\n"

    def query(
        self, 
        user_question: str, 
        n_results: int = 12, 
        max_tokens: int = config.CLAUDE_MAX_TOKENS, 
        model: str = config.CLAUDE_MODEL, 
        mode: str = "single", 
        chat_history: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        
        # 1. Kontext mit den neuen REFERENZ-IDs bauen
        context = self.create_context_prompt(user_question, n_results)
        system_prompt = config.SYSTEM_PROMPT
        
        # 2. User-Prompt zusammensetzen
        user_prompt_parts = []
        if mode == "multi" and chat_history:
            user_prompt_parts.append(self.format_chat_history(chat_history))
        
        user_prompt_parts.append(f"Hier ist der relevante Kontext für die Beantwortung:\n{context}")
        user_prompt_parts.append(f"Frage des Nutzers: {user_question}")
        user_prompt = "\n\n".join(user_prompt_parts)
        
        result = {"answer": "", "plot_created": False, "plot_result": None, "plot_data": None}
        
        try:
            # 3. Haupt-Anfrage an Claude
            msg = self.client.messages.create(
                model=model, 
                max_tokens=max_tokens, 
                system=system_prompt, 
                messages=[{"role": "user", "content": user_prompt}]
            )
            answer = msg.content[0].text
            result["answer"] = answer

            # 4. Prüfen ob ein Plot generiert werden soll
            if any(k in user_question.lower() for k in ["plot", "grafik", "diagramm", "plotte", "zeichne"]):
                plot_data = self._extract_plot_data_from_answer(user_question, answer)
                
                if plot_data:
                    name_map = {
                        "hometech": "Home Tech", "home tech": "Home Tech",
                        "digital_solutions": "Digital Solutions", "digital solutions": "Digital Solutions"
                    }
                    
                    # Mapping der Units für Konsistenz
                    if "units" in plot_data and isinstance(plot_data["units"], list):
                        plot_data["units"] = [name_map.get(u.lower(), u) for u in plot_data["units"]]
                    
                    # Mapping der Values Keys (Monate/Units)
                    if "values" in plot_data and isinstance(plot_data["values"], dict):
                        new_values = {}
                        for k, v in plot_data["values"].items():
                            new_key = name_map.get(str(k).lower(), k)
                            new_values[new_key] = v
                        plot_data["values"] = new_values

                    # Nur erlaubte Parameter an Plot-Funktion übergeben
                    allowed = {'labels', 'values', 'units', 'title'}
                    filtered = {k: v for k, v in plot_data.items() if k in allowed}
                    
                    # Grafik generieren (animate=False für stabilere Anzeige im ersten Schritt)
                    result["plot_result"] = self.plot_function(**filtered, animate=False)
                    result["plot_created"] = True
                    result["plot_data"] = filtered
            
            return result

        except Exception as e:
            result["answer"] = f"Fehler bei der Verarbeitung: {str(e)}"
            return result

    def _extract_plot_data_from_answer(self, query: str, answer: str) -> Optional[Dict]:
        """
        Extrahiert die Rohdaten für den Plot aus der Antwort und dem Kontext.
        """
        # Wir geben einen etwas kleineren Kontext mit, um Token zu sparen
        mini_context = self.create_context_prompt(query, n_results=4)
        
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

ANTWORT: {answer}
KONTEXT: {mini_context}
"""
        try:
            msg = self.client.messages.create(
                model=config.CLAUDE_MODEL, 
                max_tokens=1000, 
                messages=[{"role": "user", "content": extraction_prompt}]
            )
            text = re.sub(r"json?|```", "", msg.content[0].text.strip())
            return json.loads(text)
        except:
            return None