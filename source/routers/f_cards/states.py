from aiogram.fsm.state import State, StatesGroup


class Deck_creating(StatesGroup):
    name = State()
    tag = State()


class Deck_options(StatesGroup):
    deck_name = State()
    enter = State()
    deck_entered = State()
    card_entered = State()
    card_question = State()
    card_answer = State()
    deck_deleting = State()
    card_deleting = State()
    card_changing = State()
    training = State()
    training_start = State()
