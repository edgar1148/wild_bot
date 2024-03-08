import os
import sys
import logging
import asyncio

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from bot.handlers import router
from bot.database import setup_database

load_dotenv()

TOKEN = os.getenv("TOKEN")

async def main():
    
    await setup_database()

    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except SystemExit:
        print("Bot stopped")
 