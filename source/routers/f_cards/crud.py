from collections import deque
from random import shuffle
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import types
from source.config.db.models.deck import Deck
from source.config.db.models.flash_card import Flash_card
from sqlalchemy import select
from sqlalchemy.orm import selectinload

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
        user = await session.scalar(select(User).where(User.tg_id == msg.from_user.id))  # type: ignore
        new_deck = Deck(
            name=data["name"],
            tag=data["tag"],
            recent_interaction=None,
            user_id=user.id,  # type: ignore
        )
        session.add(new_deck)
        await session.commit()
    except Exception:
        return False
    return True


async def validate_name_uniqueness_or_existing(
    msg: types.Message, deck_name: str, session: AsyncSession, flag: str
) -> bool | list[Flash_card] | str:
    try:
        if not deck_name:
            return False
        stmt = select(Deck).join(Deck.user).where(User.tg_id == msg.from_user.id)  # type: ignore
        decks = await session.scalars(stmt)
        for deck in decks:
            if deck.name == deck_name.strip():
                if flag == "unique":
                    return False
                else:
                    cards = []
                    try:
                        stmt = (
                            select(Flash_card)
                            .join(Flash_card.deck)
                            .where(Deck.id == deck.id)
                        )
                        cards = list(await session.scalars(stmt))
                    except Exception:
                        cards = []
                    return cards if cards else "empty"
    except Exception:
        return False
    if flag == "unique":
        return True
    else:
        return False


async def validate_unique_question_field(
    msg: types.Message,
    question: str,
    deck_name: str,
    session: AsyncSession,
) -> bool:
    try:
        stmt = select(Flash_card).join(Flash_card.deck).where(Deck.name == deck_name)
        cards = await session.scalars(stmt)
        for card in cards:
            if card.question == question:
                return False
    except Exception:
        return False
    return True


async def create_card(
    data: dict[str, str],
    session: AsyncSession,
) -> bool:
    try:
        deck = await session.scalar(select(Deck).where(Deck.name == data["deck_name"]))
        card = Flash_card(
            deck_id=deck.id,  # type: ignore
            question=data["card_question"],
            answer=data["card_answer"],
        )
        session.add(card)
        await session.commit()
    except Exception:
        return False
    return True


async def delete_deck(
    msg: types.Message,
    deck_name: str,
    session: AsyncSession,
) -> bool:
    try:
        stmt = (
            select(Deck)
            .where(Deck.name == deck_name)
            .join(Deck.user)
            .where(User.tg_id == msg.from_user.id)  # type: ignore
            .options(
                selectinload(Deck.cards),
            )
        )  # type: ignore
        deck = await session.scalar(stmt)
        if deck and deck.cards:
            for card in deck.cards:
                await session.delete(card)
        await session.delete(deck)
        await session.commit()
    except Exception:
        return False
    return True


async def card_with_question_exist(
    msg: types.Message,
    question: str,
    deck_name: str,
    session: AsyncSession,
) -> None | Flash_card:
    try:
        stmt = (
            select(Flash_card)
            .join(Flash_card.deck)
            .where(Deck.name == deck_name)
            .where(Flash_card.question == question)
        )
        card = await session.scalar(stmt)
    except Exception:
        return None
    return card  # type: ignore


async def delete_card(
    msg: types.Message,
    card_question: str,
    session: AsyncSession,
) -> bool:
    try:
        stmt = select(Flash_card).where(Flash_card.question == card_question)
        card = await session.scalar(stmt)
        await session.delete(card)
        await session.commit()
    except Exception:
        return False
    return True


async def get_training_deque(
    deck_name: str,
    session: AsyncSession,
) -> None | deque[Flash_card]:
    try:
        stmt = select(Flash_card).join(Flash_card.deck).where(Deck.name == deck_name)
        cards = list(await session.scalars(stmt))
    except Exception:
        return None
    shuffle(cards)
    return deque((cards)) if cards else None  # type: ignore
