# Setup Hilfe

## Virtuelle Python Umgebung aktivieren

### Warum eine virtuelle Umgebung?

Die virtuelle Umgebung isoliert die Python-Pakete dieses Projekts von deinem System, um Konflikte mit anderen Projekten zu vermeiden. Es ist wie ein separater Arbeitsplatz für dieses spezifische Projekt mit seinen eigenen Werkzeugen.

### IDE-Setup (empfohlen)

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

**Manuelle Aktivierung im Terminal**

Falls du direkt im Terminal arbeiten möchtest, kannst du die virtuelle Umgebung mit folgenden Befehlen aktivieren:

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS/Linux oder Windows mit Bash:**
```bash
source .venv/bin/activate
```


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
