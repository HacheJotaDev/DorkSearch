#!/usr/bin/env bash
# Instalador de URLs Google Dorks Searcher para Linux (Debian/Ubuntu y derivados).
set -e

echo "[*] Instalando dependencias..."
sudo apt-get update -y
sudo apt-get install -y python3 python3-pip
python3 -m pip install --user requests

echo "[*] Listo. Prueba con:"
echo "    python3 dork_search.py --list-dorks"
echo "    python3 dork_search.py 'inurl:index.php?id='"
