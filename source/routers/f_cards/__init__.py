from aiogram import Router
from .handlers import router as f_cards_router

router = Router(name=__name__)
router.include_router(f_cards_router)
