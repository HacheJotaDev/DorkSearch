#!/usr/bin/env python3
"""
Google Dorks URL Searcher — OSINT / authorized reconnaissance.

Returns URLs matching Google dorks (including SQLi-style dorks). Intended for
authorized security testing, bug bounty within program scope, and defensive
research ONLY. This tool SEARCHES and RETURNS URLs; it does not exploit
anything. Exploiting a third-party system (including extracting its database
via SQLi) is out of scope and belongs only on systems you own or are
authorized to test.

Proxy support: rotating proxies, one per line, in the format
    IP:PORT:USER:PASSWORD        (authenticated residential proxy)
    IP:PORT                      (unauthenticated)
Requests go through a randomly chosen proxy.

Backends:
  --api-key / --cx   Google Custom Search JSON API (reliable; needs a key,
                     100 free queries/day at programmablesearchengine).
  (default)          Direct scraping of the Google SERP. Fragile: Google
                     frequently returns a consent/captcha page instead of
                     results, so expect empty output or a block page.

Usage:
  python3 dork_search.py "inurl:index.php?id="
  python3 dork_search.py --category sqli --max 50 --proxies proxies.txt
  python3 dork_search.py --dorks dorks.txt --out urls.txt --scope scope.txt
  python3 dork_search.py --list-dorks
"""

import argparse
import random
import re
import sys
import time
import urllib.parse

try:
    import requests
except ImportError:  # pragma: no cover
    sys.exit("This tool needs the `requests` package (pre-installed on Kortix).")

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

# --------------------------------------------------------------------------- #
# Dork presets (public, standard reconnaissance queries — GHDB-style)
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
        'intitle:"panel de control" login',
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
# Proxy handling
# --------------------------------------------------------------------------- #


def proxy_to_url(proxy: str) -> str:
    """Convert IP:PORT[:USER[:PASSWORD]] into an http:// proxy URL."""
    parts = proxy.strip().split(":", 3)
    if len(parts) == 2:
        return f"http://{parts[0]}:{parts[1]}"
    if len(parts) == 4:
        ip, port, user, password = parts
        return f"http://{user}:{password}@{ip}:{port}"
    raise ValueError(f"bad proxy format (want IP:PORT[:USER[:PASSWORD]]): {proxy!r}")


def load_proxies(path: str) -> list[str]:
    with open(path) as fh:
        lines = [ln.strip() for ln in fh if ln.strip() and not ln.startswith("#")]
    return lines


def pick_proxy(proxies: list[str]) -> dict | None:
    """Return a requests `proxies` dict for a random proxy, or None."""
    if not proxies:
        return None
    url = proxy_to_url(random.choice(proxies))
    return {"http": url, "https": url}


# --------------------------------------------------------------------------- #
# Google backends
# --------------------------------------------------------------------------- #


def google_cse(api_key: str, cx: str, query: str, proxies, num: int) -> list[str]:
    url = "https://www.googleapis.com/customsearch/v1"
    params = {"key": api_key, "cx": cx, "q": query, "num": min(num, 10)}
    resp = requests.get(url, params=params, proxies=proxies, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    return [item.get("link", "") for item in data.get("items", []) if item.get("link")]


_RESULT_RE = re.compile(r"/url\?q=(?P<url>[^&\"]+)")


def scrape_google(query: str, proxies, num: int) -> list[str]:
    url = "https://www.google.com/search"
    params = {"q": query, "num": num, "hl": "en"}
    headers = {"User-Agent": UA}
    resp = requests.get(url, params=params, headers=headers, proxies=proxies, timeout=15)
    if resp.status_code != 200:
        return []
    urls = []
    for m in _RESULT_RE.finditer(resp.text):
        u = urllib.parse.unquote(m.group("url"))
        if u and "google." not in u:
            urls.append(u)
    # De-duplicate while preserving order
    seen = set()
    out = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


# --------------------------------------------------------------------------- #
# Scope filtering
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


def main() -> None:
    ap = argparse.ArgumentParser(description="Google dorks URL searcher (OSINT / authorized recon).")
    ap.add_argument("query", nargs="?", help="A single dork, e.g. 'inurl:index.php?id='")
    ap.add_argument("--category", choices=list(DORKS), help="Run a preset dork category")
    ap.add_argument("--dorks", help="File with one dork per line")
    ap.add_argument("--list-dorks", action="store_true", help="Print the built-in dorks and exit")
    ap.add_argument("--out", help="Write URLs to this file")
    ap.add_argument("--max", type=int, default=10, help="Max results per dork (default 10)")
    ap.add_argument("--proxies", help="File of proxies, one per line (IP:PORT[:USER[:PASSWORD]])")
    ap.add_argument("--api-key", help="Google Custom Search API key")
    ap.add_argument("--cx", help="Google Custom Search engine id (with --api-key)")
    ap.add_argument("--scope", help="Only keep URLs whose host is in this file (authorized targets)")
    ap.add_argument("--delay", type=float, default=1.0, help="Seconds between queries (default 1.0)")
    args = ap.parse_args()

    if args.list_dorks:
        for cat, ds in DORKS.items():
            print(f"[{cat}]")
            for d in ds:
                print(f"  {d}")
        return

    if args.category:
        queries = DORKS[args.category]
    elif args.dorks:
        with open(args.dorks) as fh:
            queries = [ln.strip() for ln in fh if ln.strip() and not ln.startswith("#")]
    elif args.query:
        queries = [args.query]
    else:
        ap.error("provide a query, --category, or --dorks")

    if args.api_key and not args.cx:
        ap.error("--api-key requires --cx")
    if args.cx and not args.api_key:
        ap.error("--cx requires --api-key")

    proxies = load_proxies(args.proxies) if args.proxies else []
    scope = load_scope(args.scope) if args.scope else []

    if proxies:
        print(f"[*] Loaded {len(proxies)} proxies (rotating)")
    if scope:
        print(f"[*] Scope filter active: {len(scope)} domain(s)")

    collected = []
    for i, q in enumerate(queries, 1):
        px = pick_proxy(proxies)
        print(f"[*] ({i}/{len(queries)}) dork: {q}")
        try:
            if args.api_key:
                urls = google_cse(args.api_key, args.cx, q, px, args.max)
            else:
                urls = scrape_google(q, px, args.max)
        except Exception as exc:  # noqa: BLE001
            print(f"    ! failed: {exc}")
            urls = []

        filtered = [u for u in urls if in_scope(u, scope)]
        collected.extend(filtered)
        for u in filtered:
            print(f"    {u}")
        if not filtered:
            print("    (no results — Google may have blocked the scrape; try --api-key/--cx)")
        time.sleep(args.delay)

    # De-duplicate globally
    seen, final = set(), []
    for u in collected:
        if u not in seen:
            seen.add(u)
            final.append(u)

    print(f"\n[*] Total unique URLs: {len(final)}")
    if args.out:
        with open(args.out, "w") as fh:
            fh.write("\n".join(final) + ("\n" if final else ""))
        print(f"[*] Wrote {args.out}")


if __name__ == "__main__":
    main()
