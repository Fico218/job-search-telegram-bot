# Bot de Busqueda de Empleo para Telegram

Busca automaticamente trabajos en LinkedIn, Indeed, InfoJobs, Computrabajo y GetOnBoard, y los envia a tu Telegram cada hora.

## Instalacion

### 1. Requisitos previos
- Python 3.10 o superior
- Una cuenta de Telegram

### 2. Clonar/descargar el proyecto

```
cd job-bot
```

### 3. Instalar dependencias

```
pip install -r requirements.txt
```

### 4. Configurar el bot

#### Paso A: Crear el bot en Telegram
1. Abre Telegram y busca `@BotFather`
2. Escribe `/newbot`
3. Sigue las instrucciones y copia el **token** que te da

#### Paso B: Obtener tu Chat ID
1. Busca `@userinfobot` en Telegram
2. Escribe `/start`
3. Copia el numero de **Id** que te muestra

#### Paso C: Crear el archivo .env
Copia el archivo de ejemplo y edita tus datos:

```
copy .env.example .env
```

Edita `.env` con tus datos reales:

```
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrSTUvwxyz
TELEGRAM_CHAT_ID=123456789
SEARCH_KEYWORDS=desarrollador python,backend developer,python developer
LOCATION=Mexico
SEARCH_INTERVAL_HOURS=1
REMOTE_ONLY=false
```

### 5. Ejecutar el bot

```
python bot.py
```

## Comandos del bot

| Comando | Descripcion |
|---------|-------------|
| `/start` | Ver instrucciones |
| `/buscar` | Buscar trabajos ahora mismo |
| `/estado` | Ver configuracion actual |
| `/keywords python,react` | Cambiar palabras clave |
| `/ayuda` | Ver esta ayuda |

## Estructura del proyecto

```
job-bot/
  bot.py              - Bot principal + scheduler
  storage.py          - Evita enviar duplicados
  requirements.txt    - Dependencias Python
  .env                - Tu configuracion (NO compartir)
  scrapers/
    base.py           - Clase base
    linkedin.py       - Scraper LinkedIn
    indeed.py         - Scraper Indeed
    infojobs.py       - Scraper InfoJobs
    computrabajo.py   - Scraper Computrabajo
    getonboard.py     - Scraper GetOnBoard
  data/
    seen_jobs.json    - Historial de trabajos vistos
```

## Notas

- Los scrapers de LinkedIn e Indeed pueden fallar ocasionalmente porque estas plataformas usan protecciones anti-bot. GetOnBoard usa una API publica y es mas estable.
- Si quieres busqueda mas robusta en LinkedIn, considera usar la libreria `jobspy` como alternativa.
- Para ejecutar 24/7, puedes usar un servidor VPS o dejarlo corriendo en tu PC.
