from aiogram import Router, types, F
from aiogram.enums import ParseMode
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State
from aiogram.utils import markdown
from .states import Survey
from .email_validate import email_validate_and_filter

router = Router(name=__name__)


@router.message(Command("cancel"), StateFilter(Survey))
async def handle_cancel_survey(msg: types.Message, state: FSMContext):
    await state.clear()
    await msg.answer(
        "Okay, let's cancel.\n\nJust let me know if you want to fill the survey!"
    )


@router.message(Command("survey"), StateFilter(default_state))
async def start_survey(msg: types.Message, state: FSMContext):
    await state.set_state(Survey.email)
    await msg.answer(
        "Good! Let's start our survey. If you want to cancel - just use the command '/cancel'.\n\nPlease write your email"
    )


@router.message(StateFilter(Survey.email), email_validate_and_filter)
async def handle_email_message(msg: types.Message, email, state: FSMContext):
    await state.update_data(email=email)
    await state.set_state(Survey.bio)
    await msg.answer(
        "Great!\nPlease write something about you now, if you don't want to write anything - just send me: 'NO'"
    )


async def save_and_send_survey_results(results: dict, msg: types.Message):
    await msg.answer(f"Your results:\nemail: {results["email"]}\nbio: {results["bio"]}")


@router.message(StateFilter(Survey.bio), ~F.text != "NO")
async def handle_bio(msg: types.Message, state: FSMContext):
    results = await state.update_data(bio=msg.text)
    await state.clear()
    await save_and_send_survey_results(results, msg)


@router.message(StateFilter(Survey.bio), F.text != "NO")
async def handle_negative_bio(msg: types.Message, state: FSMContext):
    results = await state.update_data(bio=None)
    await state.clear()
    await save_and_send_survey_results(results, msg)


@router.message(StateFilter(Survey.email))
async def handle_invalid_email_message(msg: types.Message):
    await msg.answer("Invalid email, please make sure the spelling or existing one")
