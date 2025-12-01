# Setup Hilfe

## Virtuelle Python Umgebung

Die virtuelle Umgebung isoliert die Python-Pakete dieses Projekts von deinem System, um Konflikte mit anderen Projekten zu vermeiden. Es ist wie ein separater Arbeitsplatz für dieses spezifische Projekt mit seinen eigenen Werkzeugen.

### Installation

Mit dem folgenden Befehl wird das .venv erstellt, aktiviert und Packages installiert.

```bash
python -m venv .venv && source .venv/Scripts/activate && pip install -r requirements.txt
```

Damit ist das .venv direkt im Temrinal aktiviert, allerdings noch nicht in der IDE hinterlegt.

### IDE-Setup

Es ist empfehlenswert, die erstellte virtuelle Umgebung als Standard-Interpreter in deiner IDE zu hinterlegen. Dadurch erkennt die IDE automatisch alle installierten Pakete und bietet bessere Code-Vervollständigung.

**Visual Studio Code:**

1. Öffne den Repository Ordner
2. Gib in die Suchleiste `> Python: Select Interpreter` ein
3. Wähle `Interpreterpfad eingeben`
4. Suche nach dem Pfad im .venv Ordner nach folgender Adresse oder gib diese direkt ein:
   - `.venv/Scripts/python.exe` (Windows) oder
   - `.venv/bin/python` (macOS/Linux)

**PyCharm/IntelliJ:**
   
1. Öffne den Repository Ordner als Projekt
2. Gehe zu Settings > Project Structure > Project > SDK > Add Python SDK from Disk > Existing Environment > Interpreter
3. Wähle den erstellten .venv Pfad aus mit Klick auf die drei Punkte `...`:
   - `.venv/Scripts/python.exe` (Windows) oder
   - `.venv/bin/python` (macOS/Linux).

### Troubleshooting - Globale Python Umgebungen

Es kann sein, dass trotz Setzen der virtuellen Python-Umgebung eine andere Python-Umgebung priorisiert wird (z.B. conda base). Bitte deaktiviere dementsprechend
diese globale Einstellung permanent oder temporär mit folgenden Codes:

**Conda Base temporär deaktivieren:**
```bash
# Conda Base-Umgebung verlassen
conda deactivate
```

**Conda Base permanent deaktivieren:**
```bash
# Automatische Aktivierung der Base-Umgebung beim Terminal-Start deaktivieren
conda config --set auto_activate_base false

# Überprüfung der Einstellung
conda config --show auto_activate_base
```
