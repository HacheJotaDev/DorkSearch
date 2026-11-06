# 😎 URLS GOOGLE DORKS SEARCHER 🌟💀

🔝 Un programa desarrollado para **extraer miles o millones de URLs** utilizando
dorks de Google para búsquedas personalizadas. Permite extraer URLs que sirven
para **SQL Injection** (reconocimiento) y otras búsquedas OSINT.

- **PROXY:** YES
- **PROXY TYPE:** RESIDENTIALS ROTATIVE PROXYS
- **PROXY FORMAT:** `IP:PORT:USER:PASSWORD`

---

## ⚙️ Características

- **Dorks de Google** para búsquedas personalizadas (categorías listas + dorks propios).
- **Categorías incluidas:** `sqli`, `login`, `admin`, `exposed_files`.
- **Proxies rotativos residenciales** en formato `IP:PORT:USER:PASSWORD` (también `IP:PORT` sin auth, y contraseñas con `:`).
- **Dos backends:**
  - Google Custom Search JSON API (`--api-key` / `--cx`) — fiable, 100 consultas/día gratis.
  - Scraping directo del SERP de Google (sin clave; frágil, Google suele devolver página de consentimiento).
- Filtro de **scope** (`--scope`) para limitarte a dominios autorizados.
- Deduplicación, retardo entre consultas y salida a archivo.

## 📦 Instalación

```bash
git clone https://github.com/HacheJotaDev/DorkSearch.git
cd DorkSearch
pip install requests
```

## 🚀 Uso

```bash
# Ver los dorks incluidos
python3 dork_search.py --list-dorks

# Una búsqueda con un dork concreto
python3 dork_search.py 'inurl:index.php?id='

# Toda la categoría SQLi, con proxies rotativos
python3 dork_search.py --category sqli --proxies proxies.txt --out urls.txt

# Con proxies + scope (solo objetivos autorizados)
python3 dork_search.py 'inurl:index.php?id=' --proxies proxies.txt --scope scope.txt

# Backend fiable con Google Custom Search API
python3 dork_search.py 'inurl:index.php?id=' --api-key TU_KEY --cx TU_CX

# Dorks propios desde un archivo
python3 dork_search.py --dorks dorks.txt
```

## 🔐 Formato de proxies (`proxies.txt`)

```
# una línea por proxy — formato IP:PORT:USER:PASSWORD
203.0.113.7:8080:user1:pass1
198.51.100.23:9000:user2:pass2
```

> Crea `proxies.txt` a partir de `proxies.example.txt`. No subas tus proxies
> reales al repositorio (está en `.gitignore`).

## 🧭 Dorks incluidos

- **sqli** — `inurl:"index.php?id="`, `inurl:"product.php?id="`, `inurl:"news.php?id="`, etc.
- **login** — `inurl:"login.php"`, `intitle:"sign in" inurl:"admin"`, etc.
- **admin** — `intitle:"admin panel"`, `inurl:"admin.php"`, etc.
- **exposed_files** — `intitle:"index of" ".env"`, `filetype:sql inurl:dump`, etc.

## ⚠️ Uso autorizado

Esta herramienta es para **reconocimiento OSINT**, auditorías de seguridad
**autorizadas**, bug bounty **dentro del scope** del programa e investigación
defensiva. Busca y lista URLs; **no explota nada**. Explotar sistemas de
terceros sin autorización es ilegal. Usa `--scope` para restringirte a tus
objetivos autorizados.

## 📝 Nota sobre Google

El scraping directo de Google devuelve frecuentemente una página de
consentimiento (sin resultados orgánicos). Para un funcionamiento fiable usa
`--api-key` / `--cx` con una [Google Custom Search JSON API](https://developers.google.com/custom-search/v1/overview).
