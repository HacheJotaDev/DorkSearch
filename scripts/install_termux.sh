#!/usr/bin/env bash
# Instalador de URLs Google Dorks Searcher para Termux (Android).
set -e

echo "[*] Actualizando paquetes..."
pkg update -y && pkg upgrade -y

echo "[*] Instalando Python..."
pkg install -y python git

echo "[*] Instalando requests..."
python -m pip install requests

echo "[*] Listo. Prueba con:"
echo "    python dork_search.py --list-dorks"
echo "    python dork_search.py 'inurl:index.php?id='"
