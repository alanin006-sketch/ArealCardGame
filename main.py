# main.py
import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from config.settings import BOT_TOKEN
from database.db import init_db

from game.matchmaker import Matchmaker  # ← импорт

# Получаем порт от Render
PORT = int(os.environ.get("PORT", 10000))
RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL", "https://arealcardgame.onrender.com")
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"{RENDER_EXTERNAL_URL}{WEBHOOK_PATH}"

bot = Bot(token=BOT_TOKEN)
from bot.handlers import start, game
dp = Dispatcher()

async def on_startup(app: web.Application):
    await init_db()
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(app: web.Application):
    await bot.delete_webhook(drop_pending_updates=True)

def main():
    # Создаём matchmaker с ботом
    matchmaker = Matchmaker(bot)

    # Устанавливаем его в game.router
    game.set_matchmaker(matchmaker)

    dp.include_router(start.router)
    dp.include_router(game.router)

    app = web.Application()
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_shutdown)

    async def health_check(request):
        return web.json_response({"status": "ok", "webhook_url": WEBHOOK_URL})

    async def set_webhook(request):
        await bot.set_webhook(WEBHOOK_URL)
        return web.json_response({"status": "webhook set", "url": WEBHOOK_URL})

    app.router.add_get("/", health_check)
    app.router.add_get("/setwebhook", set_webhook)

    web.run_app(app, host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    main()
