from aiogram import Router
from .handle_first_time import router as start_router

router = Router(name=__name__)
router.include_router(start_router)
