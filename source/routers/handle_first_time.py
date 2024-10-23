from aiogram import Router, types
from aiogram.filters import CommandStart
from sqlalchemy.ext.asyncio import AsyncSession

from source.routers.root_crud import remember_user

router = Router(name=__name__)


@router.message(CommandStart())
async def handle_first_time(msg: types.Message, session: AsyncSession):
    await msg.answer(
        "Hello!\nI'll help you with tasks and learning something.\nTo see additional information use: '/help'"
    )
    try:
        await remember_user(msg, session)
    except Exception as err:
        raise err
