from typing import Callable, Awaitable
from aiogram import BaseMiddleware, types
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class DBMiddleware(BaseMiddleware):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory

    async def __call__(
        self,
        handler: Callable[[types.TelegramObject, dict[str, any]], Awaitable[any]],  # type: ignore
        event: types.TelegramObject,
        data: dict[str, any],  # type: ignore
    ) -> any:  # type: ignore

        async with self.session_factory() as session:
            data["session"] = session
            return await handler(event, data)
