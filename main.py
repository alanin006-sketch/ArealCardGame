import asyncio
import logging
from aiogram import Bot, Dispatcher
from config.settings import BOT_TOKEN
from database.db import init_db
from bot.handlers import start, game

# Глобальный экземпляр бота для использования в других модулях (например, matchmaker)
bot = Bot(token=BOT_TOKEN)

async def main():
    logging.basicConfig(level=logging.INFO)
    await init_db()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(start.router)
    dp.include_router(game.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
