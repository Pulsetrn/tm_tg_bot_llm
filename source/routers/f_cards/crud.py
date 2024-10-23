from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import types
from source.config.db.models.deck import Deck
from source.config.db.models.profile import Profile
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload

from source.config.db.models.user import User


async def get_user_decks(
    msg: types.Message, session: AsyncSession
) -> list[Deck] | bool:
    try:
        stmt = select(Deck).order_by(Deck.id).join(Deck.user).where(User.tg_id == msg.from_user.id)  # type: ignore
        decks = await session.scalars(stmt)
    except Exception:
        return False
    return list(decks) if decks else False


async def add_deck_to_user(
    msg: types.Message,
    data: dict[str, str],
    session: AsyncSession,
) -> bool:
    try:
        new_deck = Deck(
            name=data["name"],
            tag=data["tag"],
        )
        session.add(new_deck)
        await session.commit()
    except Exception:
        return False
    return True
