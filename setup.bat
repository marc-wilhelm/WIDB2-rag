@echo off
echo ============================================
echo RAG-Projekt Setup
echo ============================================
echo.

REM Check ob Python installiert ist
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python ist nicht installiert!
    echo Bitte Python 3.11 oder 3.12 von python.org installieren
    pause
    exit /b 1
)

echo [OK] Python gefunden:
python --version
echo.

REM Frage User nach Setup-Art
echo Welches Setup moechtest du?
echo [1] Lokal mit venv (schnell, fuer Entwicklung)
echo [2] Docker (langsam, aber fuer Team identisch)
echo [3] Beides (empfohlen)
echo.
set /p choice="Deine Wahl (1/2/3): "

if "%choice%"=="1" goto local_setup
if "%choice%"=="2" goto docker_setup
if "%choice%"=="3" goto both_setup

echo Ungueltige Eingabe!
pause
exit /b 1

:local_setup
echo.
echo ============================================
echo Lokales venv Setup
echo ============================================

REM Check ob venv existiert
if exist "venv\" (
    echo [INFO] venv existiert bereits
) else (
    echo [INFO] Erstelle venv...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] venv erstellen fehlgeschlagen!
        pause
        exit /b 1
    )
    echo [OK] venv erstellt
)

REM Aktiviere venv und installiere Packages
echo [INFO] Installiere Packages...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo [ERROR] Package-Installation fehlgeschlagen!
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Lokales Setup fertig!
echo.
echo Zum Aktivieren: venv\Scripts\activate
echo Dann: streamlit run src/app.py
echo.
pause
exit /b 0

:docker_setup
echo.
echo ============================================
echo Docker Setup
echo ============================================

REM Check ob Docker läuft
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker ist nicht installiert oder laeuft nicht!
    echo Bitte Docker Desktop installieren und starten
    pause
    exit /b 1
)

echo [OK] Docker gefunden
echo [INFO] Baue Docker Image (dauert 5-10 Minuten beim ersten Mal)...

docker-compose build

if %errorlevel% neq 0 (
    echo [ERROR] Docker Build fehlgeschlagen!
    echo Tipp: Versuche Python 3.12 statt 3.13 im Dockerfile
    pause
    exit /b 1
)

echo [INFO] Starte Container...
docker-compose up -d

if %errorlevel% neq 0 (
    echo [ERROR] Container Start fehlgeschlagen!
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Docker Setup fertig!
echo.
echo Container läuft im Hintergrund
echo Zum Stoppen: docker-compose down
echo Zum Testen: docker exec -it rag-app bash
echo.
pause
exit /b 0

:both_setup
echo.
echo ============================================
echo Vollständiges Setup (lokal + Docker)
echo ============================================

REM Erst lokales Setup
call :local_setup

echo.
echo ============================================
echo Jetzt Docker Setup...
echo ============================================
echo [INFO] Druecke eine Taste um mit Docker fortzufahren
echo (Das dauert 5-10 Minuten)
pause

call :docker_setup

exit /b 0