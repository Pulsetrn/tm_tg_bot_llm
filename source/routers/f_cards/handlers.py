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
