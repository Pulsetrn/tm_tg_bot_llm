from aiogram import F, Router, types
from langchain_community.chat_models.gigachat import GigaChat
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

from loadotenv import sber

router = Router(name=__name__)

llm = GigaChat(credentials=sber, verify_ssl_certs=False)
conversation = ConversationChain(
    llm=llm, verbose=False, memory=ConversationBufferMemory()
)


@router.message(F.text)
async def handle_user_message(msg: types.Message):
    text = msg.text
    if any("?" == char for char in text):  # type: ignore
        response = conversation.predict(input=text)
        await msg.answer(response)
    else:
        await msg.answer(
            "Do you want something?\n\nIf you don't know what you want, you can use '/help' command to see the list of the existing commands"
        )


@router.message()
async def handle_other_message(msg: types.Message):
    await msg.answer(
        "I don't understand.\n\nIf you want something and don't know - use '/help' to see the list of the commands."
    )
