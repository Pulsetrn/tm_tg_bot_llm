import asyncio
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram import Bot, Dispatcher
import logging
from source.middlewares.db_middleware import DBMiddleware
from source.routers import router as handlers_router
from loadotenv import bot_token, db_url
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


bot = Bot(
    token=bot_token,  # type: ignore
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher()
dp.include_router(handlers_router)


async def main():
    logging.basicConfig(level=logging.DEBUG)
    engine = create_async_engine(
        url=db_url,  # type: ignore
        echo=False,
        pool_size=5,
        max_overflow=10,
    )
    session_factory = async_sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )
    dp.update.middleware(DBMiddleware(session_factory=session_factory))
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
