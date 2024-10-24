from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from sqlalchemy.ext.asyncio import AsyncSession

from source.routers.f_cards.crud import (
    add_deck_to_user,
    card_with_question_exist,
    create_card,
    delete_card,
    delete_deck,
    get_training_deque,
    get_user_decks,
    validate_name_uniqueness_or_existing,
    validate_unique_question_field,
)
from source.routers.f_cards.states import Deck_creating, Deck_options


class LexMessages:
    leave_message: str = "If you want to leave - just write '/leave'."


router = Router(name=__name__)


@router.message(Command("show_decks"), StateFilter(default_state))
async def handle_show_decks(
    msg: types.Message, state: FSMContext, session: AsyncSession
):
    if decks := await get_user_decks(msg, session):
        decks = [f"{num}) {deck.name}, tag: {deck.tag if deck.tag else "---"}" for num, deck in enumerate(decks, 1)]  # type: ignore
        await state.set_state(Deck_options.enter)
        await msg.answer(
            f"{'\n'.join(decks)}\n\nIf you want to look at the cards in some deck - just write the name of the deck!\n\nIf you no longer want to work with decks or view them, just write '/leave'."
        )
    else:
        await msg.answer(
            "Have you created decks before?\n\nIf not, then use the '/create_deck' command to be able to view them."
        )


@router.message(Command("leave"), StateFilter(Deck_options))
async def handle_leave_from_decks_view(msg: types.Message, state: FSMContext):
    await state.clear()
    await msg.answer(
        "Okay!\n\nIf you want something else just warn me.",
        reply_markup=types.ReplyKeyboardRemove(),
    )


async def show_deck_cards(
    msg: types.Message,
    deck_name: str,
    state: FSMContext,
    session: AsyncSession,
):
    if cards := await validate_name_uniqueness_or_existing(msg, deck_name, session, "exist"):  # type: ignore
        await state.set_state(Deck_options.deck_entered)
        cards_text = (
            "\n".join([f"{num}) {card.question}" for num, card in enumerate(cards, 1)])
            if cards != "empty"
            else False
        )
        await msg.answer(
            f"Good!\nEntering the {deck_name} deck...\n\n{deck_name}:\n\n{cards_text}\n\n{LexMessages.leave_message}\n\nIf you want to see the list of activities - just write '/activities'",
            reply_markup=types.ReplyKeyboardRemove(),
        )
    else:
        await msg.answer(
            "Something went wrong while returning.\n\nTry to use '/show_decks' and then choose your deck.\n\nIn case of failure, contact @Georpl_tme.",
            reply_markup=types.ReplyKeyboardRemove(),
        )


@router.message(StateFilter(Deck_options.enter))
async def handle_deck_name_choosing(
    msg: types.Message,
    state: FSMContext,
    session: AsyncSession,
):
    deck_name = msg.text
    if cards := await validate_name_uniqueness_or_existing(msg, deck_name, session, "exist"):  # type: ignore
        await state.update_data(deck_name=deck_name)
        await state.set_state(Deck_options.deck_entered)
        cards_text = (
            "\n".join([f"{num}) {card.question}" for num, card in enumerate(cards, 1)])
            if cards != "empty"
            else False
        )
        if cards_text:
            await msg.answer(
                f"Good!\nEntering the {deck_name} deck...\n\n{deck_name}:\n\n{cards_text}\n\n{LexMessages.leave_message}\n\nIf you want to see the list of activities - just write '/activities'"
            )
        else:
            await msg.answer(
                f"Good!\nEntering the deck...\n\n{deck_name}:\n\nYou haven't created cards for this deck yet\n\nDo you want to create some?\nIf yes - just write '/create_new_card'.\n\nAlso you can leave the deck, for this write - '/leave'\n\nIf you want to delete this deck - just write '/delete_deck'"
            )
    else:
        await msg.answer(
            "Something went wrong.\n\nCheck the spelling of the name or the existence of a deck with the same name."
        )


@router.message(Command("train_deck"), StateFilter(Deck_options.deck_entered))
async def handle_train_deck_activity(msg: types.Message, state: FSMContext):
    await state.set_state(Deck_options.training_start)
    await msg.answer(
        "Alright, you sure that you want to start training this deck?",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Yes")], [KeyboardButton(text="No")]],
        ),
    )


@router.message(
    StateFilter(Deck_options.training_start), F.text != "No", F.text != "Yes"
)
async def handle_invalid_train_answer(msg: types.Message):
    await msg.answer("Please, choose or write 'Yes' or 'No'.")


@router.message(StateFilter(Deck_options.training_start), F.text == "No")
async def handle_negative_train_answer(
    msg: types.Message,
    state: FSMContext,
    session: AsyncSession,
):
    data = await state.get_data()
    await msg.answer("Good!\nThen I'll return you into the choosed deck!")
    await show_deck_cards(msg, data["deck_name"], state, session)


@router.message(StateFilter(Deck_options.training_start), F.text == "Yes")
async def handle_positive_train_answer(
    msg: types.Message,
    state: FSMContext,
    session: AsyncSession,
):
    data = await state.get_data()
    if cards_to_train := await get_training_deque(data["deck_name"], session):
        await state.set_state(Deck_options.training)
        await state.update_data(training=cards_to_train)
        await msg.answer(
            f"Good!\nLet's start\n\nHere's your card:\nQuestion: {cards_to_train[0].question}\n\nType your understanding - is it 'Good' or 'Bad'?",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="Good")], [KeyboardButton(text="Bad")]],
            ),
        )
    else:
        await msg.answer(
            "Something went wrong.\n\nI'm sending you back into decks.\nTry again.\n\nIn case of failure, contact @Georpl_tme."
        )
        await show_deck_cards(msg, data["deck_name"], state, session)


@router.message(StateFilter(Deck_options.training), F.text != "Good", F.text != "Bad")
async def handle_training_message(msg: types.Message):
    await msg.answer("Please write 'Good' or 'Bad'")


@router.message(StateFilter(Deck_options.training), F.text == "Good")
async def handle_good_training_message(
    msg: types.Message, state: FSMContext, session: AsyncSession
):
    data = await state.get_data()
    data["training"].popleft()
    await msg.answer("Good!\n\nGo on, the next question!")
    await send_next_question(msg, state, session)


@router.message(StateFilter(Deck_options.training), F.text == "Bad")
async def handle_bad_training_message(
    msg: types.Message, state: FSMContext, session: AsyncSession
):
    data = await state.get_data()
    bad_question = data["training"].popleft()
    data["training"].append(bad_question)
    await msg.answer(
        "Okay, it's not a problem.\nYou'll see this question one more time soon!\n\nGo on, the next question!"
    )
    await send_next_question(msg, state, session)


async def send_next_question(
    msg: types.Message,
    state: FSMContext,
    session: AsyncSession,
):
    data = await state.get_data()
    if data["training"]:
        await msg.answer(
            f"Question: {data["training"][0].question}\n\nType - 'Bad' or 'Good'"
        )
    else:
        await msg.answer(
            "You've done all the cards in this deck. Well done!\n\nReturning you back..."
        )
        await state.update_data(training=None)
        await show_deck_cards(msg, data["deck_name"], state, session)


@router.message(Command("activities"), StateFilter(Deck_options.deck_entered))
async def handle_ask_for_activities(
    msg: types.Message,
):
    await msg.answer(
        "You can carry out the following activities:\n1) Create new card - '/create_new_card'\n2) You can choose card and work with this card, for this just write certain question of concrete card to enter it\n3) Delete this deck - '/delete_deck'\n4) Work with deck - '/train_deck'.\nDon't know what work with deck means? - '/train_deck_activity' is the answer!"
    )


@router.message(Command("train_deck_activity"), StateFilter(Deck_options.deck_entered))
async def handle_ask_for_train_deck(
    msg: types.Message,
):
    await msg.answer(
        "Work with deck it's a process where you need to answer on the cards that you've created in random order and mark your level of understanding. You have two levels: bad and good understanding, if you have bad understanding - then this concrete card will appear one more time and so on until you figure it out and give good."
    )


@router.message(Command("delete_deck"), StateFilter(Deck_options.deck_entered))
async def handle_deck_delition(
    msg: types.Message,
    state: FSMContext,
):
    await state.set_state(Deck_options.deck_deleting)
    await msg.answer(
        "Are you sure?\n\nYou'll also delete all of your cards in this deck!",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Yes")], [KeyboardButton(text="No")]],
        ),
    )


@router.message(
    StateFilter(Deck_options.deck_deleting), F.text != "No", F.text != "Yes"
)
async def handle_invalid_deck_delition_answer(msg: types.Message):
    await msg.answer("Please, choose or write 'Yes' or 'No'.")


@router.message(StateFilter(Deck_options.deck_deleting), F.text == "No")
async def handle_negative_deck_delition_answer(
    msg: types.Message,
    state: FSMContext,
    session: AsyncSession,
):
    data = await state.get_data()
    await msg.answer("Good!\nThen I'll return you into the choosed deck!")
    await show_deck_cards(msg, data["deck_name"], state, session)


@router.message(StateFilter(Deck_options.deck_deleting), F.text == "Yes")
async def handle_positive_deck_delition(
    msg: types.Message,
    state: FSMContext,
    session: AsyncSession,
):
    data = await state.get_data()
    if await delete_deck(msg, data["deck_name"], session):
        await state.clear()
        await msg.answer(
            "The deck has been successfully removed.\n\nIf you want something else: just warn me!"
        )
    else:
        await state.clear()
        await msg.answer(
            text="An error occurred while deleting the deck. Please, try again.\n\nIn case of failure, contact @Georpl_tme",
            reply_markup=types.ReplyKeyboardRemove(),
        )


@router.message(Command("create_new_card"), StateFilter(Deck_options.deck_entered))
async def handle_creating_new_card_survey_starting(
    msg: types.Message,
    state: FSMContext,
):
    await state.set_state(Deck_options.card_question)
    await msg.answer(
        f"Good!\n\nNow write the main question of your card.\nRemember the question must be unique!\n\nRecomendations:\nTry to write your question shorter - this will improve the user experience in the future. Also, write only one question on the topic on one card.\n\n{LexMessages.leave_message}"
    )


@router.message(StateFilter(Deck_options.deck_entered), F.text)
async def handle_card_choosing(
    msg: types.Message,
    state: FSMContext,
    session: AsyncSession,
):
    data = await state.get_data()
    if card := await card_with_question_exist(
        msg, msg.text, data["deck_name"], session  # type: ignore
    ):
        await state.set_state(Deck_options.card_entered)
        await state.update_data(card_entered=card.question)
        await msg.answer(
            f"Entereing card...\n\nQuestion: {card.question}\nAnswer: {card.answer}\nCreated at: {card.created_at}\n\nTo see the list of activities with this card - use '/card_activities'"
        )
    else:
        await msg.answer(
            "The card with this name doesn't exist, check the spelling.\n\nIf you want to do other activity - write '/activities' to see the list of all actions.\n\nIf you something else - firstly leave from deck - '/leave'"
        )


@router.message(Command("card_activities"), StateFilter(Deck_options.card_entered))
async def handle_card_activities_question(msg: types.Message):
    await msg.answer(
        "You can carry out the following activities:\n\n1) Delete the card - '/delete_card'\n2) Change the card fields - '/change_card'"
    )


@router.message(Command("change_card"), StateFilter(Deck_options.card_entered))
async def handle_card_change(msg: types.Message, state: FSMContext):
    await state.set_state(Deck_options.card_changing)
    await msg.answer(
        "Are you sure that you want to change something?",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Yes")], [KeyboardButton(text="No")]],
        ),
    )


@router.message(
    StateFilter(Deck_options.card_changing), F.text != "No", F.text != "Yes"
)
async def handle_invalid_input_card_changing(msg: types.Message):
    await msg.answer("Please write 'Yes' or 'No'")


@router.message(StateFilter(Deck_options.card_changing), F.text == "No")
async def handle_positive_input_card_changing(
    msg: types.Message,
    state: FSMContext,
    session: AsyncSession,
):
    data = await state.get_data()
    await msg.answer("Good!\nThen I'll return you into the choosed deck!")
    await show_deck_cards(msg, data["deck_name"], state, session)


@router.message(StateFilter(Deck_options.card_changing), F.text == "Yes")
async def handle_negative_input_card_changing(
    msg: types.Message,
    state: FSMContext,
    session: AsyncSession,
):
    data = await state.get_data()
    if await delete_card(msg, data["card_entered"], session):
        await state.set_state(Deck_options.card_question)
        await msg.answer("Okay, then write the new unique question for your card")
    else:
        await msg.answer(
            "Something went wrong.\n\nTry again.\n\nIn case of failure, contact @Georpl_tme."
        )


@router.message(Command("delete_card"), StateFilter(Deck_options.card_entered))
async def handle_card_delition(
    msg: types.Message,
    state: FSMContext,
):
    await state.set_state(Deck_options.card_deleting)
    await msg.answer(
        "Are you sure?",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Yes")], [KeyboardButton(text="No")]],
        ),
    )


@router.message(
    StateFilter(Deck_options.card_deleting), F.text != "No", F.text != "Yes"
)
async def handle_invalid_card_delition_answer(msg: types.Message):
    await msg.answer("Please, choose or write 'Yes' or 'No'.")


@router.message(StateFilter(Deck_options.card_deleting), F.text == "No")
async def handle_negative_card_delition_answer(
    msg: types.Message,
    state: FSMContext,
    session: AsyncSession,
):
    data = await state.get_data()
    await msg.answer("Good!\nThen I'll return you into the choosed deck!")
    await show_deck_cards(msg, data["deck_name"], state, session)


@router.message(StateFilter(Deck_options.card_deleting), F.text == "Yes")
async def handle_positive_card_delition(
    msg: types.Message,
    state: FSMContext,
    session: AsyncSession,
):
    data = await state.get_data()
    if await delete_card(msg, data["card_entered"], session):
        await msg.answer(
            "Card has been successfully removed.\n\nI'll return you into the choosed deck!"
        )
        await show_deck_cards(msg, data["deck_name"], state, session)
    else:
        await msg.answer(
            text="An error occurred while deleting the deck. I'll return you into the choosed. Try again.\n\nIn case of failure, contact @Georpl_tme",
            reply_markup=types.ReplyKeyboardRemove(),
        )
        await show_deck_cards(msg, data["deck_name"], state, session)


@router.message(StateFilter(Deck_options.card_question))
async def handle_card_question_creating(
    msg: types.Message,
    state: FSMContext,
    session: AsyncSession,
):
    deck_name = await state.get_data()
    if await validate_unique_question_field(msg, msg.text, deck_name["deck_name"], session):  # type: ignore
        await state.update_data(card_question=msg.text)
        await state.set_state(Deck_options.card_answer)
        await msg.answer("Great!\n\nNow, please write the answer for the card")


@router.message(StateFilter(Deck_options.card_answer))
async def handle_card_answer_creating(
    msg: types.Message,
    state: FSMContext,
    session: AsyncSession,
):
    data = await state.update_data(card_answer=msg.text)
    if await create_card(data, session):
        await msg.answer(
            "Your card has been successfully created!\n\nReturning back..."
        )
        await show_deck_cards(msg, data["deck_name"], state, session)
    else:
        await msg.answer(
            "An error occurred while creating new card. Please, try again.\n\nIn case of failure, contact @Georpl_tme."
        )


@router.message(Command("cancel"), StateFilter(Deck_creating))
async def handle_deck_creating_cancel(msg: types.Message, state: FSMContext):
    await state.clear()
    await msg.answer(
        "Okay.\n\nIf you want something else just warn me or use '/help' to see the list of commands."
    )


@router.message(Command("create_deck"), StateFilter(default_state))
async def handle_create_deck(msg: types.Message, state: FSMContext):
    await msg.answer(
        "Good!\n\nWhat's the name of the deck do you want to have?\nAnd remember name of the deck must be unique!\n\nIf you want to cancel the deck creating just write - '/cancel'.",
        reply_markup=types.ReplyKeyboardRemove(),
    )
    await state.set_state(Deck_creating.name)


@router.message(StateFilter(Deck_creating.name))
async def handle_choosing_name(
    msg: types.Message, state: FSMContext, session: AsyncSession
):
    if await validate_name_uniqueness_or_existing(msg, msg.text, session, "unique"):  # type: ignore
        await state.update_data(name=msg.text)
        await msg.answer(
            "Cool!\n\nIf you want to somehow conveniently structure your decks in the future, I recommend using a tag. If you don't want to add a tag to your deck, just write: 'No'."
        )
        await state.set_state(Deck_creating.tag)
    else:
        await msg.answer(
            "The deck name you entered probably already exists. Please use a unique name.\n\nPlease, try again.\n\nIn case of failure, contact @Georpl_tme."
        )


@router.message(StateFilter(Deck_creating.tag))
async def handle_choosing_tag(
    msg: types.Message, state: FSMContext, session: AsyncSession
):
    data = await state.update_data(tag=msg.text)
    await state.clear()
    if await add_deck_to_user(msg, data, session):
        await msg.answer("Your results have been successfully recorded.")
    else:
        await msg.answer(
            "An error occurred while creating new deck. Please, try again.\n\n In case of failure, contact @Georpl_tme."
        )


@router.message(StateFilter(Deck_creating.tag), F.text == "No")
async def handle_negative_choosing_tag(
    msg: types.Message,
    state: FSMContext,
    session: AsyncSession,
):
    data = await state.update_data(tag=None)
    await state.clear()
    if await add_deck_to_user(msg, data, session):
        await msg.answer("Your results have been successfully recorded.")
    else:
        await msg.answer(
            "An error occurred while creating new deck. Please, try again.\n\nIn case of failure, contact @Georpl_tme."
        )
