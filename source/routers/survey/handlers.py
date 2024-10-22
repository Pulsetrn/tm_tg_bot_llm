from aiogram import Router, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.utils import markdown
from sqlalchemy.ext.asyncio import AsyncSession
from source.config.db.helpers import db_helper
from source.routers.survey.crud import record_survey
from .states import Survey
from .email_validate import email_validate_and_filter

router = Router(name=__name__)


@router.message(Command("cancel"), StateFilter(Survey))
async def handle_cancel_survey(msg: types.Message, state: FSMContext):
    await state.clear()
    await msg.answer(
        "Okay, let's cancel.\n\nJust let me know if you want to fill the survey!",
        reply_markup=types.ReplyKeyboardRemove(),
    )


@router.message(Command("survey"), StateFilter(default_state))
async def start_survey(msg: types.Message, state: FSMContext):
    await state.set_state(Survey.email)
    await msg.answer(
        "Good! Let's start our survey. If you want to cancel - just use the command '/cancel'.\n\nPlease write your email",
        reply_markup=types.ReplyKeyboardRemove(),
    )


@router.message(StateFilter(Survey.email), email_validate_and_filter)
async def handle_email_message(msg: types.Message, email, state: FSMContext):
    await state.update_data(email=email)
    await state.set_state(Survey.bio)
    await msg.answer(
        "Great!\nPlease write something about you now, if you don't want to write anything - just send me: 'No'"
    )


async def save_and_send_survey_results(results: dict, msg: types.Message):
    pass


@router.message(StateFilter(Survey.bio), ~F.text != "No")
async def handle_bio(msg: types.Message, state: FSMContext):
    await state.update_data(bio=msg.text)
    msg.answer(
        "Good!\nDo you want to share some of your interests. follow this form:\ninterest1,interest2,interest3 and so on, the separator would be ',' without spaces!\n\nIf you don't want to share anything - just write: 'No'",
    )
    await state.set_state(Survey.range_of_interests)


@router.message(StateFilter(Survey.bio), F.text != "No")
async def handle_negative_bio(msg: types.Message, state: FSMContext):
    await state.update_data(bio=None)
    msg.answer(
        "Good!\nDo you want to share some of your interests. follow this form:\ninterest1,interest2,interest3 and so on, the separator would be ',' without spaces!\n\nIf you don't want to share anything - just write: 'No'",
    )
    await state.set_state(Survey.range_of_interests)


@router.message(StateFilter(Survey.range_of_interests), F.text != "No")
async def handle_range_of_interests(msg: types.Message, state: FSMContext):
    await state.update_data(range_of_interests=msg.text)
    await msg.answer(
        "Well.\n\nThen, do you want to see the results of the survey?",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Yes")], [KeyboardButton(text="No")]],
        ),
    )
    await state.set_state(Survey.finish)


@router.message(StateFilter(Survey.range_of_interests), F.text != "No")
async def handle_negative_range_of_interests(msg: types.Message, state: FSMContext):
    await state.update_data(range_of_interests=None)
    await msg.answer(
        "Well.\n\nThen, do you want to see the results of the survey?",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Yes")], [KeyboardButton(text="No")]],
        ),
    )
    await state.set_state(Survey.finish)


@router.message(StateFilter(Survey.finish), F.text == "Yes", db_helper.session_getter)
async def handle_finish(msg: types.Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    await state.clear()
    text = markdown.text(
        "Your results:",
        "",
        markdown.text("Email:", markdown.hbold(data["email"])),
        markdown.text("Bio:", markdown.hbold(data["bio"])),
        sep="\n",
    )
    await msg.answer(text=text)
    if await record_survey(msg, data, session):
        await msg.answer(
            text="your results have been successfully recorded",
            reply_markup=types.ReplyKeyboardRemove(),
        )
    else:
        await msg.answer(
            text="An error occurred while recording data. If you filled out the form previously, please delete the data first to fill it out again. Otherwise, try again. In case of failure, contact @Georpl_tme",
            reply_markup=types.ReplyKeyboardRemove(),
        )


@router.message(StateFilter(Survey.finish), F.text == "No", db_helper.session_getter)
async def handle_negative_finish(
    msg: types.Message,
    state: FSMContext,
    session: AsyncSession,
):
    data = await state.get_data()
    await state.clear()
    if await record_survey(msg, data, session):
        await msg.answer(
            text="your results have been successfully recorded",
            reply_markup=types.ReplyKeyboardRemove(),
        )
    else:
        await msg.answer(
            text="An error occurred while recording data. If you filled out the form previously, please delete the data first to fill it out again. Otherwise, try again. In case of failure, contact @Georpl_tme",
            reply_markup=types.ReplyKeyboardRemove(),
        )


@router.message(StateFilter(Survey.email))
async def handle_invalid_email_message(msg: types.Message):
    await msg.answer("Invalid email, please make sure the spelling or existing one")
