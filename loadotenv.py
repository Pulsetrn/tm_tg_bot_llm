import os
import dotenv


# TODO: переписать на pydantic или хотя бы на dataclass
dotenv.load_dotenv()
bot_token = os.getenv("TG_BOT_KEY")
db_url = os.getenv("TG_BOT_DB")
sber = os.getenv("SBER")

# EXAMPLE (dataclass)

# from dataclasses import dataclass
# from environs import Env


# @dataclass
# class TgBot:
#     token: str


# @dataclass
# class Config:
#     tg_bot: TgBot


# def load_config(path: str | None = None) -> Config:
#     env = Env()
#     env.read_env(path)
#     return Config(tg_bot=TgBot(token=env('BOT_TOKEN')))