from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import types
from source.config.db.models.profile import Profile


async def record_survey(
    msg: types.Message,
    data: dict[str, any],  # type: ignore
    session: AsyncSession,
) -> bool:
    try:
        new_profile = Profile(
            tg_id=msg.from_user.id,
            email=data["email"],
            bio=data["bio"],
            range_of_interests=data["range_of_interests"],
        )
        session.add(new_profile)
        await session.commit()
    except Exception:
        return False
    return True
