from aiogram import Router
from .handlers import router as daily_router

router = Router(name=__name__)
router.include_router(daily_router)
