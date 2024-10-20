import asyncio
import os
from aiogram import Bot, Dispatcher, types
import logging
import requests
import dotenv

dotenv.load_dotenv()
bot_token = os.getenv("TG_BOT_KEY")

bot = Bot(token=bot_token) # type: ignore
dp = Dispatcher()

async def main():
    logging.basicConfig(level=logging.DEBUG)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
