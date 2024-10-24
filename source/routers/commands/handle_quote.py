from aiogram import Router, types
from aiogram.filters import Command
import requests

router = Router(name=__name__)


@router.message(Command("quote"))
async def get_quote(msg: types.Message):
    try:
        data = requests.get("https://zenquotes.io/api/random").json()
        await msg.answer(
            f'Quote: {data[0]["q"]}\nAuthor: {data[0]["a"]}',
        )
    except Exception as err:
        await msg.answer(f"Something went wrong\nError: {err}")
