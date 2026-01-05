import pytest
from pathlib import Path
import tempfile
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.MarkdownCleaner import MarkdownCleaner, MultiMarkdownCleaner


class TestExtractMonthFromHeading:

    def test_standard_format(self):
        """Prüft ob Monat und Jahr aus einer Standard-Überschrift korrekt extrahiert werden."""
        cleaner = MarkdownCleaner("dummy.md")
        result = cleaner.extract_month_from_heading("## Januar 2023: Stabile Ausgangslage")
        assert result == "Januar 2023"

    def test_all_months(self):
        """Validiert dass alle 12 Monate (Januar bis Dezember) erkannt werden."""
        cleaner = MarkdownCleaner("dummy.md")
        months = ["Januar", "Februar", "März", "April", "Mai", "Juni",
                  "Juli", "August", "September", "Oktober", "November", "Dezember"]

        for month in months:
            heading = f"## {month} 2023: Test"
            result = cleaner.extract_month_from_heading(heading)
            assert result == f"{month} 2023"

    def test_different_years(self):
        """Prüft ob verschiedene Jahreszahlen korrekt verarbeitet werden."""
        cleaner = MarkdownCleaner("dummy.md")
        for year in [2022, 2023, 2024, 2025]:
            result = cleaner.extract_month_from_heading(f"## Januar {year}: Test")
            assert result == f"Januar {year}"

    def test_no_month(self):
        """Stellt sicher dass None zurückgegeben wird wenn kein Monat in der Überschrift ist."""
        cleaner = MarkdownCleaner("dummy.md")
        result = cleaner.extract_month_from_heading("## Einleitung")
        assert result is None

    def test_invalid_format(self):
        """Prüft dass falsche Formate (z.B. Jahr vor Monat) nicht erkannt werden."""
        cleaner = MarkdownCleaner("dummy.md")
        result = cleaner.extract_month_from_heading("## Test 2023 Januar")
        assert result is None


class TestCleanAndStructure:

    @pytest.fixture
    def temp_markdown_file(self):
        """Erstellt eine temporäre Markdown-Testdatei mit typischer Struktur."""
        content = """# Hauptüberschrift

## Einleitung

Dies ist die Einleitung des Dokuments.

## Januar 2023: Stabile Ausgangslage

Im Januar 2023 war alles gut.

## Februar 2023: Rückgang

Im Februar gab es Probleme."""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name

        yield temp_path

        Path(temp_path).unlink()

    def test_basic_structure(self, temp_markdown_file):
        """Prüft ob die Markdown-Datei in die korrekten Abschnitte aufgeteilt wird."""
        cleaner = MarkdownCleaner(temp_markdown_file, source_identifier='test')
        result = cleaner.clean_and_structure()

        assert len(result) == 3
        assert result[0]['type'] == 'einleitung'
        assert result[1]['type'] == 'monatsbericht'
        assert result[2]['type'] == 'monatsbericht'

    def test_month_extraction(self, temp_markdown_file):
        """Validiert dass Monate aus Überschriften extrahiert und korrekt zugeordnet werden."""
        cleaner = MarkdownCleaner(temp_markdown_file, source_identifier='test')
        result = cleaner.clean_and_structure()

        assert result[0]['month'] is None
        assert result[1]['month'] == "Januar 2023"
        assert result[2]['month'] == "Februar 2023"

    def test_heading_extraction(self, temp_markdown_file):
        """Stellt sicher dass Überschriften ohne ## korrekt extrahiert werden."""
        cleaner = MarkdownCleaner(temp_markdown_file, source_identifier='test')
        result = cleaner.clean_and_structure()

        assert result[0]['heading'] == "Einleitung"
        assert result[1]['heading'] == "Januar 2023: Stabile Ausgangslage"

    def test_text_extraction(self, temp_markdown_file):
        """Prüft ob der Textinhalt jedes Abschnitts korrekt extrahiert wird."""
        cleaner = MarkdownCleaner(temp_markdown_file, source_identifier='test')
        result = cleaner.clean_and_structure()

        assert "Einleitung des Dokuments" in result[0]['text']
        assert "Januar 2023 war alles gut" in result[1]['text']

    def test_source_identifier(self, temp_markdown_file):
        """Validiert dass der Source-Identifier an alle Paragraphen weitergegeben wird."""
        cleaner = MarkdownCleaner(temp_markdown_file, source_identifier='finance')
        result = cleaner.clean_and_structure()

        assert all(p['source'] == 'finance' for p in result)

    def test_paragraph_ids(self, temp_markdown_file):
        """Prüft ob Paragraph-IDs sequenziell von 0 an vergeben werden."""
        cleaner = MarkdownCleaner(temp_markdown_file, source_identifier='test')
        result = cleaner.clean_and_structure()

        assert result[0]['paragraph_id'] == 0
        assert result[1]['paragraph_id'] == 1
        assert result[2]['paragraph_id'] == 2

    def test_empty_sections_ignored(self):
        """Stellt sicher dass leere Abschnitte ignoriert und nicht als Paragraphen gespeichert werden."""
        content = """# Hauptüberschrift

## Einleitung

Text

## 

## Januar 2023: Test

Mehr Text"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name

        cleaner = MarkdownCleaner(temp_path, source_identifier='test')
        result = cleaner.clean_and_structure()

        assert len(result) == 2

        Path(temp_path).unlink()


class TestMultiMarkdownCleaner:

    @pytest.fixture
    def temp_markdown_files(self):
        """Erstellt zwei temporäre Markdown-Dateien für Multi-Source-Tests."""
        content1 = """# Doc 1

## Einleitung

Text 1

## Januar 2023: Test

Content 1"""

        content2 = """# Doc 2

## Einleitung

Text 2

## Februar 2024: Test

Content 2"""

        files = []
        for content in [content1, content2]:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
                f.write(content)
                files.append(f.name)

        yield files

        for f in files:
            Path(f).unlink()

    def test_process_multiple_files(self, temp_markdown_files):
        """Prüft ob mehrere Markdown-Dateien verarbeitet und zusammengeführt werden."""
        configs = [
            {'path': temp_markdown_files[0], 'source_id': 'doc1'},
            {'path': temp_markdown_files[1], 'source_id': 'doc2'}
        ]

        multi_cleaner = MultiMarkdownCleaner(configs)
        result = multi_cleaner.process_all()

        assert len(result) == 4

    def test_global_paragraph_ids(self, temp_markdown_files):
        """Validiert dass Paragraph-IDs über alle Dateien hinweg eindeutig und sequenziell sind."""
        configs = [
            {'path': temp_markdown_files[0], 'source_id': 'doc1'},
            {'path': temp_markdown_files[1], 'source_id': 'doc2'}
        ]

        multi_cleaner = MultiMarkdownCleaner(configs)
        result = multi_cleaner.process_all()

        ids = [p['paragraph_id'] for p in result]
        assert ids == [0, 1, 2, 3]

    def test_get_paragraphs_by_source(self, temp_markdown_files):
        """Prüft ob Paragraphen nach Source-ID gefiltert werden können."""
        configs = [
            {'path': temp_markdown_files[0], 'source_id': 'doc1'},
            {'path': temp_markdown_files[1], 'source_id': 'doc2'}
        ]

        multi_cleaner = MultiMarkdownCleaner(configs)
        multi_cleaner.process_all()

        doc1_paragraphs = multi_cleaner.get_paragraphs_by_source('doc1')
        doc2_paragraphs = multi_cleaner.get_paragraphs_by_source('doc2')

        assert len(doc1_paragraphs) == 2
        assert len(doc2_paragraphs) == 2
        assert all(p['source'] == 'doc1' for p in doc1_paragraphs)
        assert all(p['source'] == 'doc2' for p in doc2_paragraphs)