from aiogram.fsm.state import State, StatesGroup


class Deck_creating(StatesGroup):
    name = State()
    tag = State()