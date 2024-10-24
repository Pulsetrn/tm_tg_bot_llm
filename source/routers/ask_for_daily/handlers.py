from aiogram import Router, types
from aiogram.filters import Command

router = Router(name=__name__)


@router.message(Command("get_daily"))
async def handle_get_dailt(msg: types.Message):
    await msg.answer(
        "Here's your daily problems!\nTry to solve them all, good luck!\n\nhttps://problems.ru/view_random.php"
    )
