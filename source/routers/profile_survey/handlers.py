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

from source.routers.profile_survey.crud import (
    delete_user_profile,
    get_user_profile_data,
    is_user_exist,
    record_survey,
)
from source.routers.profile_survey.validators.interests_validate import (
    check_comma_separated_text,
)

from .states import Change_profile, Profile_survey
from .validators.email_validate import email_validate_and_filter

router = Router(name=__name__)


@router.message(Command("cancel"), StateFilter(Profile_survey))
async def handle_cancel_survey(msg: types.Message, state: FSMContext):
    await state.clear()
    await msg.answer(
        "Okay, let's cancel.\n\nJust let me know if you want to fill the survey!",
        reply_markup=types.ReplyKeyboardRemove(),
    )


@router.message(Command("cancel"), StateFilter(Change_profile))
async def handle_cancel_changing(msg: types.Message, state: FSMContext):
    await state.clear()
    await msg.answer(
        "Okay.\nDo you want something else?",
        reply_markup=types.ReplyKeyboardRemove(),
    )


@router.message(Command("show_profile_data"), StateFilter(default_state))
async def handle_check_profile_data(
    msg: types.Message, state: FSMContext, session: AsyncSession
):
    if profile_data := await get_user_profile_data(msg, session):
        text = markdown.text(
            "Your results:",
            "",
            markdown.text("Email:", markdown.hbold(profile_data.email)),
            markdown.text("Bio:", markdown.hbold(profile_data.bio)),
            markdown.text(
                "Range of interests:", markdown.hbold(profile_data.range_of_interests)
            ),
            "",
            "Do you want to delete your profile?",
            sep="\n",
        )
        await msg.answer(
            text=text,
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(text="Yes"),
                        KeyboardButton(text="No"),
                    ]
                ]
            ),
        )
        await state.set_state(Change_profile.answer)
    else:
        await msg.answer(
            "Have you already taken the survey to create a profile?\nIf not, then you cannot look at data that you have not yet written. Please first complete the survey using the command: '/profile_survey'"
        )


@router.message(StateFilter(Change_profile.deleting), F.text == "Yes")
async def handle_yes_delete_answer(
    msg: types.Message, state: FSMContext, session: AsyncSession
):
    if await delete_user_profile(msg, session):
        await msg.answer(
            "Alright.\n\nI've deleted your account\n\nDo you want something else?",
            reply_markup=types.ReplyKeyboardRemove(),
        )
        await state.clear()
    else:
        await msg.answer(
            text="An error occurred while deleting profile. Please, try again.\n\n In case of failure, contact @Georpl_tme",
            reply_markup=types.ReplyKeyboardRemove(),
        )
        await state.clear()


@router.message(StateFilter(Change_profile.deleting), F.text == "No")
async def handle_no_delete_answer(msg: types.Message, state: FSMContext):
    await state.clear()
    await msg.answer("Okay.\n\nDo you want something else?")


@router.message(StateFilter(Change_profile.deleting), F.text != "No", F.text != "Yes")
async def handle_not_no_or_yes_delete_answer(msg: types.Message):
    await msg.answer("Please answer: Yes or No.\n\nYou can also use the keyboard.")


@router.message(StateFilter(Change_profile.answer), F.text == "Yes")
async def handle_yes_answer(msg: types.Message, state: FSMContext):
    await msg.answer(
        "Okay, are you sure?",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Yes"),
                    KeyboardButton(text="No"),
                ]
            ]
        ),
    )
    await state.set_state(Change_profile.deleting)


@router.message(StateFilter(Change_profile.answer), F.text == "No")
async def handle_no_answer(msg: types.Message, state: FSMContext):
    await state.clear()
    await msg.answer("Okay.\n\nDo you want something else?")


@router.message(StateFilter(Change_profile.answer), F.text != "No", F.text != "Yes")
async def handle_not_no_or_yes_answer(msg: types.Message):
    await msg.answer("Please answer: Yes or No.\n\nYou can also use the keyboard.")


@router.message(Command("profile_survey"), StateFilter(default_state))
async def start_survey(msg: types.Message, state: FSMContext, session: AsyncSession):
    if await is_user_exist(session, msg):
        await msg.answer(
            "You have already taken the survey before. If you want to change your email, bio or circle of interests, just use the appropriate commands."
        )
        return
    await state.set_state(Profile_survey.email)
    await msg.answer(
        "Good! Let's start our survey. If you want to cancel - just use the command '/cancel'.\n\nPlease write your email",
        reply_markup=types.ReplyKeyboardRemove(),
    )


@router.message(StateFilter(Profile_survey.email), email_validate_and_filter)
async def handle_email_message(msg: types.Message, email, state: FSMContext):
    await state.update_data(email=email)
    await msg.answer(
        "Great!\nPlease write something about you now, if you don't want to write anything - just send me: 'No'"
    )
    await state.set_state(Profile_survey.bio)


@router.message(StateFilter(Profile_survey.email))
async def handle_invalid_email_message(msg: types.Message):
    await msg.answer("Invalid email, please make sure the spelling or existing one")


@router.message(StateFilter(Profile_survey.bio), F.text != "No")
async def handle_bio(msg: types.Message, state: FSMContext):
    await state.update_data(bio=msg.text)
    await msg.answer(
        "Good!\nDo you want to share some of your interests. follow this form:\ninterest1, interest2, interest3 and so on, the separator would be ',' without spaces!\n\nIf you don't want to share anything - just write: 'No'",
    )
    await state.set_state(Profile_survey.range_of_interests)


@router.message(StateFilter(Profile_survey.bio), F.text == "No")
async def handle_negative_bio(msg: types.Message, state: FSMContext):
    await state.update_data(bio=None)
    await msg.answer(
        "Good!\nDo you want to share some of your interests. follow this form:\ninterest1, interest2, interest3 and so on, the separator would be ',' without spaces!\n\nIf you don't want to share anything - just write: 'No'",
    )
    await state.set_state(Profile_survey.range_of_interests)


@router.message(
    StateFilter(Profile_survey.range_of_interests),
    F.text != "No",
    F.text.func(check_comma_separated_text),
)
async def handle_range_of_interests(msg: types.Message, state: FSMContext):
    await state.update_data(range_of_interests=msg.text)
    await msg.answer(
        "Well.\n\nThen, do you want to see the results of the survey?",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Yes")], [KeyboardButton(text="No")]],
        ),
    )
    await state.set_state(Profile_survey.finish)


@router.message(
    StateFilter(Profile_survey.range_of_interests),
    F.text != "No",
    ~F.text.func(check_comma_separated_text),
)
async def handle_invalid_range_of_interests(msg: types.Message, state: FSMContext):
    await msg.answer(
        "Please, follow this form:\ninterest1,interest2,interest3 and so on, the separator would be ',' without spaces!"
    )


@router.message(StateFilter(Profile_survey.range_of_interests), F.text == "No")
async def handle_negative_range_of_interests(msg: types.Message, state: FSMContext):
    await state.update_data(range_of_interests=None)
    await msg.answer(
        "Well.\n\nThen, do you want to see the results of the survey?",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Yes")], [KeyboardButton(text="No")]],
        ),
    )
    await state.set_state(Profile_survey.finish)


@router.message(StateFilter(Profile_survey.finish), F.text == "Yes")
async def handle_finish(msg: types.Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    await state.clear()
    text = markdown.text(
        "Your results:",
        "",
        markdown.text("Email:", markdown.hbold(data["email"])),
        markdown.text("Bio:", markdown.hbold(data["bio"])),
        markdown.text(
            "Range of interests:", markdown.hbold(data["range_of_interests"])
        ),
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


@router.message(StateFilter(Profile_survey.finish), F.text == "No")
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
