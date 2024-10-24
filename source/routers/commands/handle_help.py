from aiogram import Router, types
from aiogram.filters import Command

router = Router(name=__name__)


@router.message(Command("help"))
async def handle_help(msg: types.Message):
    await msg.answer(
        "Hello, I'm a bot that will try to help you with your studies using flashcard ideas. To get started, follow the following plan: '/start' -> '/profile_survey' -> '/show_profile_data' check the data -> start working with cards with the command '/show_decks' then follow the commands.\n\nYou can also ask any question - for this there must be a question mark in your sentence. I'll try to answer it.\n\nIf you are looking for motivation, use the '/quote' command :D!\n\nIf you want to solve a problem, use '/get_daily'"
    )
