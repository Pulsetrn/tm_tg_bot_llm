from aiogram.fsm.state import State, StatesGroup


class Profile_survey(StatesGroup):
    email = State()
    bio = State()
    range_of_interests = State()
    finish = State()


class Change_profile(StatesGroup):
    answer = State()
    deleting = State()
