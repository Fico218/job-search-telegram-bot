"""
Bot principal de Telegram para busqueda de empleos
Comandos disponibles:
  /start   - Iniciar el bot y ver instrucciones
  /buscar  - Ejecutar busqueda manual ahora
  /estado  - Ver configuracion actual del bot
  /keywords <palabras> - Cambiar palabras clave de busqueda
  /ayuda   - Ver todos los comandos
"""
import os
import asyncio
import logging
from datetime import datetime
from typing import List

from dotenv import load_dotenv
from telegram import Update, Bot
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from scrapers import (
    LinkedInScraper,
    IndeedScraper,
    InfoJobsScraper,
    ComputrabajoScraper,
    GetOnBoardScraper,
    JobOffer,
)
from storage import JobStorage

# Cargar variables de entorno
load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Configuracion global
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
SEARCH_KEYWORDS = os.getenv("SEARCH_KEYWORDS", "desarrollador python")
LOCATION = os.getenv("LOCATION", "")
REMOTE_ONLY = os.getenv("REMOTE_ONLY", "false").lower() == "true"
INTERVAL_HOURS = int(os.getenv("SEARCH_INTERVAL_HOURS", "1"))

# Estado mutable del bot (modificable con comandos)
bot_state = {
    "keywords": [kw.strip() for kw in SEARCH_KEYWORDS.split(",")],
    "location": LOCATION,
    "remote_only": REMOTE_ONLY,
    "last_search": None,
    "total_sent": 0,
    "running": True,
}

storage = JobStorage()

# Instanciar scrapers
SCRAPERS = [
    LinkedInScraper(),
    IndeedScraper(),
    InfoJobsScraper(),
    ComputrabajoScraper(),
    GetOnBoardScraper(),
]


async def run_search_and_notify(bot: Bot) -> int:
    """Ejecuta la busqueda en todas las plataformas y envia nuevas ofertas."""
    all_jobs: List[JobOffer] = []
    keywords_list = bot_state["keywords"]
    location = bot_state["location"]
    remote = bot_state["remote_only"]

    for keyword in keywords_list:
        for scraper in SCRAPERS:
            try:
                logger.info(f"Buscando '{keyword}' en {scraper.name}...")
                jobs = scraper.search(keyword, location, remote)
                all_jobs.extend(jobs)
            except Exception as e:
                logger.error(f"Error en {scraper.name}: {e}")

    new_jobs = [j for j in all_jobs if storage.is_new(j.job_id)]
    sent = 0

    for job in new_jobs:
        try:
            await bot.send_message(
                chat_id=CHAT_ID,
                text=job.to_telegram_message(),
                parse_mode="Markdown",
                disable_web_page_preview=True,
            )
            storage.mark_seen(job.job_id)
            sent += 1
            await asyncio.sleep(0.5)  # Evitar flood de Telegram
        except Exception as e:
            logger.error(f"Error enviando mensaje: {e}")

    bot_state["last_search"] = datetime.now().strftime("%d/%m/%Y %H:%M")
    bot_state["total_sent"] += sent
    logger.info(f"Busqueda completada: {sent} nuevas ofertas enviadas.")
    return sent


# ── Handlers de comandos ──────────────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Hola! Soy tu *Bot de Busqueda de Empleo*.\n\n"
        "Busco ofertas automaticamente cada hora en:\n"
        "  LinkedIn, Indeed, InfoJobs, Computrabajo y GetOnBoard\n\n"
        "*Comandos disponibles:*\n"
        "/buscar - Ejecutar busqueda ahora mismo\n"
        "/estado - Ver configuracion actual\n"
        "/keywords <palabras> - Cambiar palabras clave\n"
        "/ayuda - Ver esta ayuda\n\n"
        "El bot esta activo y buscara trabajos automaticamente."
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def cmd_buscar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Iniciando busqueda en todas las plataformas... Espera un momento.")
    bot = context.bot
    sent = await run_search_and_notify(bot)
    if sent == 0:
        await update.message.reply_text(
            "No se encontraron nuevas ofertas en este momento. Ya te notifique todo lo disponible."
        )
    else:
        await update.message.reply_text(f"Busqueda completada. Se enviaron *{sent}* nuevas ofertas.", parse_mode="Markdown")


async def cmd_estado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keywords_str = ", ".join(bot_state["keywords"])
    last = bot_state["last_search"] or "Nunca"
    remote_str = "Si" if bot_state["remote_only"] else "No"
    location_str = bot_state["location"] or "Global/Sin filtro"

    text = (
        f"*Estado del Bot*\n\n"
        f"Palabras clave: `{keywords_str}`\n"
        f"Ubicacion: {location_str}\n"
        f"Solo remoto: {remote_str}\n"
        f"Ultima busqueda: {last}\n"
        f"Total ofertas enviadas: {bot_state['total_sent']}\n"
        f"Ofertas vistas (historico): {storage.count()}\n"
        f"Frecuencia: cada {INTERVAL_HOURS} hora(s)"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def cmd_keywords(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Uso: /keywords <palabra1>, <palabra2>, ...\n"
            "Ejemplo: /keywords desarrollador python, backend developer"
        )
        return
    new_keywords = " ".join(context.args).split(",")
    bot_state["keywords"] = [kw.strip() for kw in new_keywords if kw.strip()]
    keywords_str = ", ".join(bot_state["keywords"])
    await update.message.reply_text(
        f"Palabras clave actualizadas:\n`{keywords_str}`", parse_mode="Markdown"
    )


async def cmd_ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await cmd_start(update, context)


# ── Scheduler ─────────────────────────────────────────────────────────────────

async def scheduled_search(bot: Bot):
    logger.info("Ejecutando busqueda programada...")
    sent = await run_search_and_notify(bot)
    if sent > 0:
        logger.info(f"Scheduler: {sent} nuevas ofertas enviadas.")
    else:
        logger.info("Scheduler: Sin nuevas ofertas.")


def main():
    if not BOT_TOKEN:
        raise ValueError("Falta TELEGRAM_BOT_TOKEN en el archivo .env")
    if not CHAT_ID:
        raise ValueError("Falta TELEGRAM_CHAT_ID en el archivo .env")

    # Crear aplicacion de Telegram
    app = Application.builder().token(BOT_TOKEN).build()

    # Registrar comandos
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("buscar", cmd_buscar))
    app.add_handler(CommandHandler("estado", cmd_estado))
    app.add_handler(CommandHandler("keywords", cmd_keywords))
    app.add_handler(CommandHandler("ayuda", cmd_ayuda))

    # Configurar scheduler
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        scheduled_search,
        "interval",
        hours=INTERVAL_HOURS,
        args=[app.bot],
        id="job_search",
    )
    scheduler.start()

    logger.info(f"Bot iniciado. Buscando cada {INTERVAL_HOURS} hora(s).")
    logger.info(f"Palabras clave: {bot_state['keywords']}")
    logger.info(f"Ubicacion: {bot_state['location'] or 'Global'}")

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
