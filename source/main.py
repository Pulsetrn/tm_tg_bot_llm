import asyncio
import os
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
import logging
import requests
import dotenv

dotenv.load_dotenv()
bot_token = os.getenv("TG_BOT_KEY")

bot = Bot(
    token=bot_token,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)  # type: ignore
dp = Dispatcher()

tasks = {}


@dp.message(Command("create_task"))
async def create_task(msg: types.Message):
    await msg.answer(msg.from_user.id, "Good!\nWrite the name of your task")


# TODO: аналогично start
@dp.message(Command("help"))
async def handle_help(msg: types.Message):
    pass


# TODO: поприветствовать + отослать к комманде help
@dp.message(CommandStart())
async def handle_start(msg: types.Message):
    await msg.answer(f"Hello {msg.from_user.full_name}!")


@dp.message(Command("quote"))
async def get_quote(msg: types.Message):
    try:
        data = requests.get("https://zenquotes.io/api/random").json()
        await msg.answer(
            f'Quote: {data[0]["q"]}\nAuthor: {data[0]["a"]}',
        )
    except Exception as err:
        await msg.answer(f"Something went wrong\nError: {err}")


# TODO: обработать такой кейс корректно
@dp.message()
async def asnwer_something(msg: types.Message, result: str):
    await msg.answer(f"Do you want anything else? {result}")


async def main():
    logging.basicConfig(level=logging.DEBUG)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
