from aiogram.fsm.state import StatesGroup, State


class Survey(StatesGroup):
    email = State()
    bio = State()
    finish = State()