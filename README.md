# 😎 URLS GOOGLE DORKS SEARCHER 🌟💀

🔝 Un programa desarrollado para **extraer miles o millones de URLs** utilizando
dorks de Google para búsquedas personalizadas. Permite extraer URLs que sirven
para **SQL Injection** (reconocimiento) y otras búsquedas OSINT.

**100% por consola** — sin interfaz gráfica — y **multiplataforma**:
Linux, Windows y **Termux (Android)**.

- **PROXY:** YES
- **PROXY TYPE:** RESIDENTIALS ROTATIVE PROXYS
- **PROXY FORMAT:** `IP:PORT:USER:PASSWORD`

---

## 📦 Instalación

La única dependencia es Python 3.8+ y el paquete `requests`.

### 🐧 Linux (Debian/Ubuntu y derivados)

```bash
sudo apt update && sudo apt install -y python3 python3-pip
python3 -m pip install --user requests
```

En Fedora/RedHat:

```bash
sudo dnf install -y python3 python3-pip
python3 -m pip install --user requests
```

### 🪟 Windows

1. Instala Python desde https://www.python.org/downloads/
   (marca **"Add Python to PATH"** durante la instalación).
2. Abre **PowerShell** o **CMD** y ejecuta:

```powershell
py -m pip install requests
```

También puedes instalar Python con `winget`:

```powershell
winget install Python.Python.3.12
```

### 📱 Termux (Android)

Instala [Termux](https://f-droid.org/packages/com.termux/) (recomendado desde
F-Droid) y ejecuta:

```bash
pkg update && pkg upgrade -y
pkg install -y python
python -m pip install requests
```

> Guía completa y detallada en [`docs/TERMUX.md`](docs/TERMUX.md).

---

## 🚀 Uso (por consola)

```bash
# Ver los dorks incluidos
python3 dork_search.py --list-dorks          # Windows: py dork_search.py --list-dorks

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

En **Windows**, sustituye `python3` por `py`:

```powershell
py dork_search.py --category sqli --proxies proxies.txt
```

---

## 🔐 Proxies residenciales rotativos

Archivo `proxies.txt` (una línea por proxy):

```
# formato: IP:PORT:USER:PASSWORD   (o IP:PORT sin autenticación)
203.0.113.7:8080:user1:pass1
198.51.100.23:9000:user2:pass2
```

Cada petición sale por un proxy elegido al azar (rotativo).

**Validar tus proxies** antes de buscar:

```bash
# Solo valida el formato
python3 dork_search.py --check-proxies proxies.txt

# Prueba conectividad real (devuelve la IP de salida)
python3 dork_search.py --check-proxies proxies.txt --test
```

> Crea `proxies.txt` a partir de `proxies.example.txt`. No subas tus proxies
> reales al repositorio (está en `.gitignore`).

---

## 🧭 Dorks incluidos

| Categoría | Ejemplos |
|-----------|----------|
| `sqli` | `inurl:"index.php?id="`, `inurl:"product.php?id="`, `inurl:"news.php?id="` |
| `login` | `inurl:"login.php"`, `intitle:"sign in" inurl:"admin"` |
| `admin` | `intitle:"admin panel"`, `inurl:"admin.php"` |
| `exposed_files` | `intitle:"index of" ".env"`, `filetype:sql inurl:dump` |

---

## ⚙️ Opciones

```
query                 Un dork (p.ej. 'inurl:index.php?id=')
--category {sqli,login,admin,exposed_files}
--dorks FILE          Dorks propios (uno por línea)
--list-dorks          Lista los dorks incluidos
--out FILE            Guarda las URLs
--max N               Resultados por dork (default 10)
--proxies FILE        Archivo de proxies rotativos
--api-key / --cx      Google Custom Search JSON API
--scope FILE          Filtro a dominios autorizados
--delay SEC           Pausa entre consultas (default 1.0)
--check-proxies FILE  Valida proxies y sale
--test                Con --check-proxies: prueba conexión real
--version             Versión
```

---

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
