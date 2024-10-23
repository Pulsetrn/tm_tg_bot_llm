from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import types
from source.config.db.models.profile import Profile
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from source.config.db.models.user import User


async def get_user_profile_data(
    msg: types.Message,
    session: AsyncSession,
) -> Profile | None:
    result = None
    try:
        stmt = select(Profile).join(Profile.user).where(User.tg_id == msg.from_user.id)  # type: ignore
        result = await session.scalar(stmt)
    except Exception as err:
        raise Exception(f"Error was occurred while searching profile: {err}")
    return result if result else None


async def is_user_exist(session: AsyncSession, msg: types.Message) -> bool:
    all_user_profiles_with_users = await session.scalars(
        select(Profile).options(joinedload(Profile.user))
    )
    if msg.from_user.id in map(lambda profile: profile.user.tg_id, all_user_profiles_with_users):  # type: ignore
        return True
    return False


async def record_survey(
    msg: types.Message,
    data: dict[str, any],  # type: ignore
    session: AsyncSession,
) -> bool:
    try:
        stmt = select(User).where(User.tg_id == msg.from_user.id)  # type: ignore
        result = await session.scalar(stmt)
    except Exception as err:
        raise Exception(f"Exception was occerred while searching the user: {err}")
    try:
        new_profile = Profile(
            user_id=result.id,  # type: ignore
            email=data["email"],
            bio=data["bio"],
            range_of_interests=data["range_of_interests"],
        )
        session.add(new_profile)
        await session.commit()
    except Exception:
        return False
    return True
