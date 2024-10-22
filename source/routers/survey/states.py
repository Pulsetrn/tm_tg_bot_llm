from aiogram.fsm.state import StatesGroup, State


class Survey(StatesGroup):
    email = State()
    bio = State()
    range_of_interests = State()
    finish = State()