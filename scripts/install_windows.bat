@echo off
REM Instalador de URLs Google Dorks Searcher para Windows.
REM Requiere Python 3.8+ en el PATH (marcar "Add Python to PATH" al instalar).

echo [*] Comprobando Python...
py --version >nul 2>&1
if errorlevel 1 (
    echo [!] No se encontro Python. Instalalo desde https://www.python.org/downloads/
    echo     y marca "Add Python to PATH".
    exit /b 1
)

echo [*] Instalando requests...
py -m pip install requests

echo [*] Listo. Prueba con:
echo     py dork_search.py --list-dorks
echo     py dork_search.py "inurl:index.php?id="
