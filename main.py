import asyncio
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
import logging
import requests
from source.routers import router as handlers_router
from loadotenv import bot_token

bot = Bot(
    token=bot_token,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)  # type: ignore
dp = Dispatcher()
dp.include_router(handlers_router)


@dp.message(Command("create_task"))
async def create_task(msg: types.Message):
    await msg.answer(msg.from_user.id, "Good!\nWrite the name of your task")


# TODO: аналогично start
@dp.message(Command("help"))
async def handle_help(msg: types.Message):
    pass


@dp.message(Command("quote"))
async def get_quote(msg: types.Message):
    try:
        data = requests.get("https://zenquotes.io/api/random").json()
        await msg.answer(
            f'Quote: {data[0]["q"]}\nAuthor: {data[0]["a"]}',
        )
    except Exception as err:
        await msg.answer(f"Something went wrong\nError: {err}")


async def main():
    logging.basicConfig(level=logging.DEBUG)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
