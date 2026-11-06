# 📱 Instalación en Termux (Android)

Guía paso a paso para usar **URLs Google Dorks Searcher** en Termux, sin root.

## 1. Instalar Termux

Instala Termux desde **F-Droid** (recomendado, la versión de Play Store está
desactualizada):

- https://f-droid.org/packages/com.termux/

Abre Termux y ejecuta los siguientes comandos uno por uno.

## 2. Actualizar paquetes

```bash
pkg update && pkg upgrade -y
```

## 3. Instalar Python

```bash
pkg install -y python
```

Verifica la instalación:

```bash
python --version
```

## 4. Instalar la dependencia `requests`

```bash
python -m pip install requests
```

## 5. Descargar el repositorio

Necesitas `git` (o descárgalo como ZIP desde GitHub y descomprímelo):

```bash
pkg install -y git
git clone https://github.com/HacheJotaDev/DorkSearch.git
cd DorkSearch
```

## 6. Ejecutar

```bash
python dork_search.py --list-dorks
python dork_search.py 'inurl:index.php?id='
python dork_search.py --category sqli --proxies proxies.txt --out urls.txt
```

> En Termux el intérprete es `python` (no `python3`).

## 7. Proxies

Crea `proxies.txt` desde `proxies.example.txt`:

```bash
cp proxies.example.txt proxies.txt
# edita proxies.txt con:  nano proxies.txt
```

Valida tus proxies:

```bash
python dork_search.py --check-proxies proxies.txt --test
```

## Notas

- Termux no necesita root para esta herramienta.
- El scraping directo de Google suele devolver página de consentimiento; usa
  `--api-key` / `--cx` para resultados fiables.
