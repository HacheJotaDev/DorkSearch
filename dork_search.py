#!/usr/bin/env python3
"""
URLs Google Dorks Searcher — extrae URLs con dorks de Google (recon / OSINT).

Herramienta 100% por consola, interactiva (menú), multiplataforma:
Linux, Windows y Termux/Android. Se ejecuta SIN comandos: solo

    python dork_search.py        (Windows: py dork_search.py)

y eliges la opción en el menú.

Proxies residenciales rotativos en formato  IP:PORT:USER:PASSWORD  (o IP:PORT).

Uso: reconocimiento OSINT, auditorías de seguridad AUTORIZADAS, bug bounty
dentro del scope del programa e investigación defensiva. Busca y lista URLs;
NO explota nada.

Dependencia: requests  (python3 -m pip install requests)
"""

import random
import re
import sys
import time
import urllib.parse

try:
    import requests
except ImportError:  # pragma: no cover
    sys.exit(
        "Falta la dependencia 'requests'.\n"
        "  Linux/Termux:  python3 -m pip install requests\n"
        "  Windows:       py -m pip install requests"
    )

__version__ = "2.1.0"

BANNER = r"""
===========================================================
   URLS GOOGLE DORKS SEARCHER  v{ver}
   Extrae URLs con dorks de Google  (recon / OSINT)
   Proxies residenciales rotativos: IP:PORT:USER:PASSWORD
===========================================================
""".format(ver=__version__)

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

DORKS = {
    "sqli": [
        'inurl:"index.php?id="',
        'inurl:"product.php?id="',
        'inurl:"products.php?id="',
        'inurl:"news.php?id="',
        'inurl:"article.php?id="',
        'inurl:"articles.php?id="',
        'inurl:"page.php?id="',
        'inurl:"view.php?id="',
        'inurl:"detail.php?id="',
        'inurl:"item.php?id="',
        'inurl:"gallery.php?id="',
        'inurl:"show.php?id="',
        'inurl:"cat.php?id="',
        'inurl:"product_id="',
        'inurl:"news_id="',
        'inurl:"article_id="',
        'inurl:"id=" inurl:".php"',
        'inurl:"index.php?page="',
        'inurl:"index.php?cat="',
    ],
    "login": [
        'intitle:"login" inurl:admin',
        'inurl:"login.php"',
        'intitle:"sign in" inurl:"admin"',
        'inurl:"wp-login.php"',
    ],
    "admin": [
        'intitle:"admin panel"',
        'inurl:"admin.php"',
        'intitle:"control panel" inurl:admin',
        'inurl:"administrator" intitle:login',
    ],
    "exposed_files": [
        'intitle:"index of" ".env"',
        'intitle:"index of" "db_backup"',
        'intitle:"index of" "database.sql"',
        'inurl:"/backup/" intitle:"index of"',
        'filetype:sql inurl:dump',
    ],
}


# --------------------------------------------------------------------------- #
# Proxies
# --------------------------------------------------------------------------- #


def proxy_to_url(proxy: str) -> str:
    """Convierte IP:PORT[:USER[:PASSWORD]] en una URL http:// de proxy."""
    parts = proxy.strip().split(":", 3)
    if len(parts) == 2:
        return f"http://{parts[0]}:{parts[1]}"
    if len(parts) == 4:
        ip, port, user, password = parts
        return f"http://{user}:{password}@{ip}:{port}"
    raise ValueError(f"formato inválido (usa IP:PORT[:USER[:PASSWORD]]): {proxy!r}")


def load_proxies(path: str) -> list[str]:
    with open(path) as fh:
        return [ln.strip() for ln in fh if ln.strip() and not ln.startswith("#")]


def pick_proxy(proxies: list[str]) -> dict | None:
    if not proxies:
        return None
    url = proxy_to_url(random.choice(proxies))
    return {"http": url, "https": url}


def check_proxies(path: str, test: bool, timeout: int) -> None:
    proxies = load_proxies(path)
    if not proxies:
        print(f"\n[!] No hay proxies en {path}")
        return
    print(f"\n[*] {len(proxies)} proxies cargados desde {path}\n")
    ok = 0
    for p in proxies:
        try:
            url = proxy_to_url(p)
            if not test:
                print(f"  [FORMATO OK] {p}")
                ok += 1
                continue
            r = requests.get(
                "https://api.ipify.org?format=json",
                proxies={"http": url, "https": url},
                timeout=timeout,
            )
            print(f"  [OK]   {p}  ->  {r.json().get('ip', '?')}")
            ok += 1
        except Exception as exc:  # noqa: BLE001
            print(f"  [FAIL] {p}  ->  {exc}")
    print(f"\n[*] {ok}/{len(proxies)} proxies válidos")


# --------------------------------------------------------------------------- #
# Google backends
# --------------------------------------------------------------------------- #


def google_cse(api_key: str, cx: str, query: str, proxies, num: int) -> list[str]:
    url = "https://www.googleapis.com/customsearch/v1"
    params = {"key": api_key, "cx": cx, "q": query, "num": min(num, 10)}
    resp = requests.get(url, params=params, proxies=proxies, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    return [it.get("link", "") for it in data.get("items", []) if it.get("link")]


_RESULT_RE = re.compile(r"/url\?q=(?P<url>[^&\"]+)")


def scrape_google(query: str, proxies, num: int) -> list[str]:
    url = "https://www.google.com/search"
    params = {"q": query, "num": num, "hl": "en"}
    headers = {"User-Agent": UA}
    resp = requests.get(url, params=params, headers=headers, proxies=proxies, timeout=15)
    if resp.status_code != 200:
        return []
    out, seen = [], set()
    for m in _RESULT_RE.finditer(resp.text):
        u = urllib.parse.unquote(m.group("url"))
        if u and "google." not in u and u not in seen:
            seen.add(u)
            out.append(u)
    return out


# --------------------------------------------------------------------------- #
# Scope
# --------------------------------------------------------------------------- #


def load_scope(path: str) -> list[str]:
    with open(path) as fh:
        return [ln.strip().lower() for ln in fh if ln.strip() and not ln.startswith("#")]


def in_scope(url: str, scope: list[str]) -> bool:
    if not scope:
        return True
    host = urllib.parse.urlparse(url).netloc.lower()
    return any(host == d or host.endswith("." + d) for d in scope)


# --------------------------------------------------------------------------- #
# Motor de búsqueda compartido (menú y CLI)
# --------------------------------------------------------------------------- #


def run_queries(queries, proxies, scope, out, max_results, api_key, cx, delay):
    collected = []
    for i, q in enumerate(queries, 1):
        px = pick_proxy(proxies)
        print(f"\n[*] ({i}/{len(queries)}) dork: {q}")
        try:
            if api_key:
                urls = google_cse(api_key, cx, q, px, max_results)
            else:
                urls = scrape_google(q, px, max_results)
        except Exception as exc:  # noqa: BLE001
            print(f"    ! error: {exc}")
            urls = []

        filtered = [u for u in urls if in_scope(u, scope)]
        collected.extend(filtered)
        for u in filtered:
            print(f"    {u}")
        if not filtered:
            print("    (sin resultados — Google puede bloquear el scraping; usa la API key en el menú)")
        time.sleep(delay)

    seen, final = set(), []
    for u in collected:
        if u not in seen:
            seen.add(u)
            final.append(u)

    print(f"\n[*] Total de URLs únicas: {len(final)}")
    if out:
        with open(out, "w") as fh:
            fh.write("\n".join(final) + ("\n" if final else ""))
        print(f"[*] Guardado en {out}")
    return len(final)


# --------------------------------------------------------------------------- #
# Menú interactivo
# --------------------------------------------------------------------------- #

MENU = """  [1] Buscar con un dork propio
  [2] Categoría: SQLi
  [3] Categoría: login
  [4] Categoría: admin
  [5] Categoría: exposed_files
  [6] Ver los dorks incluidos
  [7] Validar proxies
  [8] Salir"""


def ask(prompt: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    try:
        v = input(f"  {prompt}{suffix}: ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        raise SystemExit(0)
    return v or default


def menu_search(queries) -> None:
    proxies_file = ask("Archivo de proxies (Enter = sin proxies)", "")
    scope_file = ask("Archivo de scope/dominios autorizados (Enter = sin filtro)", "")
    out_file = ask("Guardar resultados en archivo (Enter = solo pantalla)", "")
    max_s = ask("Resultados por dork", "10")
    api_key = ask("Google Custom Search API key (Enter = scraping directo)", "")
    cx = ask("Google Custom Search engine id / cx", "") if api_key else ""

    proxies = load_proxies(proxies_file) if proxies_file else []
    scope = load_scope(scope_file) if scope_file else []
    try:
        max_results = int(max_s) if max_s else 10
    except ValueError:
        max_results = 10

    run_queries(queries, proxies, scope, out_file, max_results, api_key, cx, 1.0)


def menu_validate_proxies() -> None:
    proxies_file = ask("Archivo de proxies", "proxies.txt")
    test_s = ask("¿Probar conectividad real? (s/n)", "n").lower()
    try:
        check_proxies(proxies_file, test=test_s in ("s", "si", "sí", "y", "yes"), timeout=10)
    except FileNotFoundError:
        print(f"\n[!] No existe {proxies_file}")


def interactive_menu() -> None:
    while True:
        print(BANNER)
        print(MENU)
        choice = ask("Elige una opción", "1")

        if choice == "1":
            dork = ask("Dork de búsqueda")
            if not dork:
                print("\n[!] Dork vacío, cancelado\n")
                continue
            menu_search([dork])
        elif choice == "2":
            menu_search(DORKS["sqli"])
        elif choice == "3":
            menu_search(DORKS["login"])
        elif choice == "4":
            menu_search(DORKS["admin"])
        elif choice == "5":
            menu_search(DORKS["exposed_files"])
        elif choice == "6":
            print()
            for cat, ds in DORKS.items():
                print(f"[{cat}]")
                for d in ds:
                    print(f"  {d}")
            print()
        elif choice == "7":
            menu_validate_proxies()
        elif choice in ("8", "0", "salir", "exit", "q"):
            print("\n[*] Adiós.\n")
            break
        else:
            print("\n[!] Opción no válida\n")


def main() -> None:
    interactive_menu()


if __name__ == "__main__":
    main()
