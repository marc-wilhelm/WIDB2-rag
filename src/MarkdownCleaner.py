# Schritt 2: Datenbereinigung und Chunking

from typing import List, Dict, Optional
import re


class MarkdownCleaner:
    """
    Bereinigt und extrahiert Text aus Markdown-Dateien.
    Strukturiert den Text nach Abschnitten (## Überschriften).
    Erwartet: # Einleitung + 4x ## Monatsüberschriften
    """

    def __init__(self, markdown_path: str):
        self.markdown_path = markdown_path
        self.raw_text = ""
        self.cleaned_paragraphs = []

    def extract_text(self) -> str:
        """Liest die Markdown-Datei ein."""
        with open(self.markdown_path, 'r', encoding='utf-8') as file:
            self.raw_text = file.read()
        return self.raw_text

    def extract_month_from_heading(self, heading: str) -> Optional[str]:
        """
        Extrahiert den Monat aus einer Überschrift.
        Beispiel: "## Januar 2023: Stabile Ausgangslage" -> "Januar 2023"
        """
        # Pattern: Monat Jahr (z.B. "Januar 2023", "Februar 2024")
        month_pattern = r'(Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)\s+(\d{4})'
        match = re.search(month_pattern, heading)
        if match:
            return f"{match.group(1)} {match.group(2)}"
        return None

    def clean_and_structure(self) -> List[Dict[str, str]]:
        """
        Bereinigt den Text und strukturiert ihn nach ## Überschriften.
        Erwartet Struktur:
        # Hauptüberschrift (wird ignoriert)
        ## Einleitung
        Text der Einleitung...
        ## Monat1: Titel
        Text des Monatsberichts...
        ## Monat2: Titel
        Text des Monatsberichts...

        Jeder Absatz = ## Zwischenüberschrift + Text bis zur nächsten ##
        """
        # Text extrahieren
        if not self.raw_text:
            self.extract_text()

        # Entferne die Hauptüberschrift (# mit einem Hashtag) am Anfang
        # Pattern: Entfernt die erste Zeile die mit # (aber nicht ##) beginnt
        text_without_main_heading = re.sub(r'^#\s+[^\n]+\n', '', self.raw_text, count=1)

        # Teile nach ## Zwischenüberschriften
        # Das Pattern (?=## ) bedeutet: "Teile vor jedem ##, aber behalte ## im Text"
        sections = re.split(r'\n(?=## )', text_without_main_heading)

        paragraph_id = 0

        for section in sections:
            section = section.strip()
            if not section:
                continue

            # Verarbeite nur Abschnitte die mit ## beginnen
            if section.startswith('## '):
                # Extrahiere Zwischenüberschrift (erste Zeile) und Text (alles darunter)
                lines = section.split('\n', 1)
                heading = lines[0].replace('##', '').strip()
                text = lines[1].strip() if len(lines) > 1 else ""

                # Bestimme den Typ: Einleitung oder Monatsbericht
                if 'Einleitung' in heading:
                    paragraph_type = 'einleitung'
                    month = None
                else:
                    paragraph_type = 'monatsbericht'
                    # Extrahiere Monat aus der Überschrift
                    month = self.extract_month_from_heading(heading)

                self.cleaned_paragraphs.append({
                    'paragraph_id': paragraph_id,
                    'type': paragraph_type,
                    'heading': heading,
                    'month': month,
                    'text': text,
                    'source': 'markdown'
                })
                paragraph_id += 1

        return self.cleaned_paragraphs

    def get_cleaned_data(self) -> List[Dict[str, str]]:
        """Gibt die bereinigten Daten zurück."""
        if not self.cleaned_paragraphs:
            self.clean_and_structure()
        return self.cleaned_paragraphs