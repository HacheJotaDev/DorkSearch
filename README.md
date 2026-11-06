# 😎 URLS GOOGLE DORKS SEARCHER 🌟💀

🔝 Un programa desarrollado para **extraer miles o millones de URLs** utilizando
dorks de Google para búsquedas personalizadas. Permite extraer URLs que sirven
para **SQL Injection** (reconocimiento) y otras búsquedas OSINT.

**100% por consola, con menú interactivo** — no hay que teclear comandos ni
banderas. Multiplataforma: Linux, Windows y **Termux (Android)**.

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

### 📱 Termux (Android)

Instala [Termux](https://f-droid.org/packages/com.termux/) y ejecuta:

```bash
pkg update && pkg upgrade -y
pkg install -y python
python -m pip install requests
```

> Guía completa en [`docs/TERMUX.md`](docs/TERMUX.md).

---

## 🚀 Uso (menú por consola)

Solo ejecuta el programa y navega por el menú:

```bash
python3 dork_search.py          # Linux/Termux
py dork_search.py               # Windows
```

Aparece este menú:

```
===========================================================
   URLS GOOGLE DORKS SEARCHER  v2.1.0
===========================================================

  [1] Buscar con un dork propio
  [2] Categoría: SQLi
  [3] Categoría: login
  [4] Categoría: admin
  [5] Categoría: exposed_files
  [6] Ver los dorks incluidos
  [7] Validar proxies
  [8] Salir
```

Eliges un número y respondes las preguntas (proxies, archivo de salida,
resultados por dork…). Nada de comandos que memorizar.

---

## 🔐 Proxies residenciales rotativos

Archivo `proxies.txt` (una línea por proxy):

```
# formato: IP:PORT:USER:PASSWORD   (o IP:PORT sin autenticación)
203.0.113.7:8080:user1:pass1
198.51.100.23:9000:user2:pass2
```

Cada petición sale por un proxy elegido al azar (rotativo).

**Validar proxies** desde el menú → opción `[7]`. Te pregunta el archivo y si
quieres probar conectividad real (devuelve la IP de salida de cada proxy).

> Crea `proxies.txt` a partir de `proxies.example.txt`. No subas tus proxies
> reales al repositorio (está en `.gitignore`).

---

## 🧭 Dorks incluidos

| Categoría | Ejemplos |
|-----------|----------|
| `SQLi` | `inurl:"index.php?id="`, `inurl:"product.php?id="`, `inurl:"news.php?id="` |
| `login` | `inurl:"login.php"`, `intitle:"sign in" inurl:"admin"` |
| `admin` | `intitle:"admin panel"`, `inurl:"admin.php"` |
| `exposed_files` | `intitle:"index of" ".env"`, `filetype:sql inurl:dump` |

---

## ⚠️ Uso autorizado

Esta herramienta es para **reconocimiento OSINT**, auditorías de seguridad
**autorizadas**, bug bounty **dentro del scope** del programa e investigación
defensiva. Busca y lista URLs; **no explota nada**. Explotar sistemas de
terceros sin autorización es ilegal. Usa el archivo de scope para restringirte
a tus objetivos autorizados.

## 📝 Nota sobre Google

El scraping directo de Google devuelve frecuentemente una página de
consentimiento (sin resultados orgánicos). Para un funcionamiento fiable usa
la **Google Custom Search JSON API** (te la pide el menú al buscar, o
configúrala como API key + engine id).
