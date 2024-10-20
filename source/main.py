import asyncio
import os
from aiogram import Bot, Dispatcher, types
import logging
import requests
import dotenv

dotenv.load_dotenv()
bot_token = os.getenv("TG_BOT_KEY")

bot = Bot(token=bot_token)  # type: ignore
dp = Dispatcher()


@dp.message()
async def get_quote(msg: types.Message):
    if msg.text == "Quote":
        try:
            data = requests.get("https://zenquotes.io/api/random").json()
            await msg.answer(
                f'Quote: {data[0]["q"]}\nAuthor: {data[0]["a"]}',
            )
        except Exception as err:
            await msg.answer(f"Something went wrong\nError: {err}")
    else:
        await msg.answer("Ты хочешь что-то еще?")


async def main():
    logging.basicConfig(level=logging.DEBUG)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
