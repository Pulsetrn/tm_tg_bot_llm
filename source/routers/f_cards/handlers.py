from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.utils import markdown
from sqlalchemy.ext.asyncio import AsyncSession

from source.routers.f_cards.crud import add_deck_to_user, get_user_decks
from source.routers.f_cards.states import Deck_creating
from source.routers.profile_survey.crud import (
    delete_user_profile,
    get_user_profile_data,
    is_user_exist,
    record_survey,
)
from source.routers.profile_survey.validators.interests_validate import (
    check_comma_separated_text,
)


router = Router(name=__name__)


@router.message(Command("show_decks"), StateFilter(default_state))
async def handle_show_decks(
    msg: types.Message, state: FSMContext, session: AsyncSession
):
    if decks := await get_user_decks(msg, session):
        decks = [f"{deck.id}) {deck.name}, tag: {deck.tag if deck.tag else "---"}" for deck in decks]  # type: ignore
        await msg.answer(
            f"{'\n'.join(decks)}\n\nIf you want to look at the cards in some deck - just use the id of the deck!"
        )
    else:
        await msg.answer(
            "Have you created decks before?\n\nIf not, then use the '/create_deck' command to be able to view them."
        )


@router.message(Command("create_deck"), StateFilter(default_state))
async def handle_create_deck(msg: types.Message, state: FSMContext):
    await msg.answer(
        "Good!\n\nWhat's the name of the deck do you want to have?\n\nIf you want to cancel the deck creating just write - '/cancel'",
        reply_markup=types.ReplyKeyboardRemove(),
    )
    await state.set_state(Deck_creating.name)


@router.message(Command("cancel"), StateFilter(Deck_creating))
async def handle_deck_creating_cancel(msg: types.Message, state: FSMContext):
    await state.clear()
    await msg.answer(
        "Okay.\n\nIf you want something else just warn me or use '/help' to see the list of commands."
    )


@router.message(StateFilter(Deck_creating.name))
async def handle_choosing_name(msg: types.Message, state: FSMContext):
    await state.update_data(name=msg.text)
    await msg.answer(
        "Cool!\n\nIf you want to somehow conveniently structure your decks in the future, I recommend using a tag. If you don't want to add a tag to your deck, just write: 'No'"
    )
    await state.set_state(Deck_creating.tag)


@router.message(StateFilter(Deck_creating.tag))
async def handle_choosing_tag(msg: types.Message, state: FSMContext):
    await state.update_data(name=msg.text)
    await msg.answer("")


@router.message(StateFilter(Deck_creating.tag), F.text == "No")
async def handle_negative_choosing_tag(
    msg: types.Message,
    state: FSMContext,
    session: AsyncSession,
):
    data = await state.update_data(tag=None)
    await state.clear()
    if await add_deck_to_user(msg, data, session):
        await msg.answer("Your results have been successfully recorded")
    else:
        await msg.answer(
            "An error occurred while creating new deck. Please, try again.\n\n In case of failure, contact @Georpl_tme"
        )
