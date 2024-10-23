from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import types

from source.config.db.models.user import User


async def remember_user(
    msg: types.Message,
    session: AsyncSession,
):
    try:
        new_user = User(
            fullname=msg.from_user.full_name, # type: ignore
            tg_id=msg.from_user.id, # type: ignore
        )
        session.add(new_user)
        await session.commit()
    except Exception as err:
        raise Exception(f"Error was occurred while remembering the user: {err}")
