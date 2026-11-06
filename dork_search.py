#!/usr/bin/env python3
"""
URLs Google Dorks Searcher — extrae URLs con dorks de Google (recon / OSINT).

Herramienta 100% por consola y multiplataforma (Linux, Windows, Termux/Android).
Busca y lista URLs; NO explota nada. Uso: reconocimiento OSINT, auditorías de
seguridad AUTORIZADAS, bug bounty dentro del scope e investigación defensiva.

Proxies residenciales rotativos en formato  IP:PORT:USER:PASSWORD  (o IP:PORT).

Backends:
  (default)     scraping directo del SERP de Google (sin clave; frágil).
  --api-key/--cx  Google Custom Search JSON API (fiable, 100 consultas/día).

Dependencia: requests  (python3 -m pip install requests)

Ejemplos:
  python3 dork_search.py --list-dorks
  python3 dork_search.py 'inurl:index.php?id='
  python3 dork_search.py --category sqli --proxies proxies.txt --out urls.txt
  python3 dork_search.py --check-proxies proxies.txt --test
"""

import argparse
import random
import re
import sys
import urllib.parse

try:
    import requests
except ImportError:  # pragma: no cover
    sys.exit(
        "Falta la dependencia 'requests'.\n"
        "  Linux/Termux:  python3 -m pip install requests\n"
        "  Windows:       py -m pip install requests"
    )

__version__ = "2.0.0"

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

# --------------------------------------------------------------------------- #
# Dork presets (reconocimiento estándar, estilo GHDB)
# --------------------------------------------------------------------------- #

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


def check_proxies(path: str, test: bool, timeout: int) -> int:
    """Valida el formato de proxies.txt y opcionalmente prueba conectividad."""
    proxies = load_proxies(path)
    if not proxies:
        print(f"[!] No hay proxies en {path}")
        return 1
    print(f"[*] {len(proxies)} proxies cargados desde {path}\n")
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
            ip = r.json().get("ip", "?")
            print(f"  [OK]   {p}  ->  {ip}")
            ok += 1
        except Exception as exc:  # noqa: BLE001
            print(f"  [FAIL] {p}  ->  {exc}")
    print(f"\n[*] {ok}/{len(proxies)} proxies válidos")
    return 0 if ok else 1


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
# CLI
# --------------------------------------------------------------------------- #


def cmd_search(args) -> int:
    if args.category:
        queries = DORKS[args.category]
    elif args.dorks:
        with open(args.dorks) as fh:
            queries = [ln.strip() for ln in fh if ln.strip() and not ln.startswith("#")]
    else:
        queries = [args.query]

    if args.api_key and not args.cx:
        print("[!] --api-key requiere --cx"); return 2
    if args.cx and not args.api_key:
        print("[!] --cx requiere --api-key"); return 2

    proxies = load_proxies(args.proxies) if args.proxies else []
    scope = load_scope(args.scope) if args.scope else []

    print(BANNER)
    if proxies:
        print(f"[*] {len(proxies)} proxies cargados (rotativos)")
    if scope:
        print(f"[*] Filtro de scope activo: {len(scope)} dominio(s)")

    collected = []
    for i, q in enumerate(queries, 1):
        px = pick_proxy(proxies)
        print(f"\n[*] ({i}/{len(queries)}) dork: {q}")
        try:
            if args.api_key:
                urls = google_cse(args.api_key, args.cx, q, px, args.max)
            else:
                urls = scrape_google(q, px, args.max)
        except Exception as exc:  # noqa: BLE001
            print(f"    ! error: {exc}")
            urls = []

        filtered = [u for u in urls if in_scope(u, scope)]
        collected.extend(filtered)
        for u in filtered:
            print(f"    {u}")
        if not filtered:
            print("    (sin resultados — Google puede bloquear el scraping; usa --api-key/--cx)")

    seen, final = set(), []
    for u in collected:
        if u not in seen:
            seen.add(u)
            final.append(u)

    print(f"\n[*] Total de URLs únicas: {len(final)}")
    if args.out:
        with open(args.out, "w") as fh:
            fh.write("\n".join(final) + ("\n" if final else ""))
        print(f"[*] Guardado en {args.out}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="dork_search.py",
        description="URLs Google Dorks Searcher — extrae URLs con dorks de Google (recon/OSINT).",
    )
    ap.add_argument("query", nargs="?", help="Un dork, p.ej. 'inurl:index.php?id='")
    ap.add_argument("--category", choices=list(DORKS), help="Categoría de dorks predefinida")
    ap.add_argument("--dorks", help="Archivo con un dork por línea")
    ap.add_argument("--list-dorks", action="store_true", help="Lista los dorks incluidos y sale")
    ap.add_argument("--out", help="Guarda las URLs en este archivo")
    ap.add_argument("--max", type=int, default=10, help="Resultados por dork (default 10)")
    ap.add_argument("--proxies", help="Archivo de proxies (IP:PORT[:USER[:PASSWORD]])")
    ap.add_argument("--api-key", help="Clave de Google Custom Search JSON API")
    ap.add_argument("--cx", help="ID del motor de Google Custom Search (con --api-key)")
    ap.add_argument("--scope", help="Solo conserva URLs cuyo host esté en este archivo")
    ap.add_argument("--delay", type=float, default=1.0, help="Segundos entre consultas (default 1.0)")
    ap.add_argument("--check-proxies", metavar="FILE", help="Valida un archivo de proxies y sale")
    ap.add_argument("--test", action="store_true", help="Con --check-proxies: prueba conectividad real")
    ap.add_argument("--timeout", type=int, default=10, help="Timeout por petición (default 10s)")
    ap.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = ap.parse_args()

    if args.list_dorks:
        for cat, ds in DORKS.items():
            print(f"[{cat}]")
            for d in ds:
                print(f"  {d}")
        return 0

    if args.check_proxies:
        return check_proxies(args.check_proxies, args.test, args.timeout)

    if not args.query and not args.category and not args.dorks:
        ap.error("proporciona un dork, --category o --dorks")

    return cmd_search(args)


if __name__ == "__main__":
    sys.exit(main())
