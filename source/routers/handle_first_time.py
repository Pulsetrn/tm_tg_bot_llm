from aiogram import Router, types
from aiogram.filters import Command, CommandStart
from source.config.db.helpers import db_helper


router = Router(name=__name__)


@router.message(CommandStart(), db_helper.session_getter)
async def handle_first_time(msg: types.Message):
    await msg.answer("Hello!\nI'll help you with tasks and learning something.\nTo see additional information use: '/help'")
    