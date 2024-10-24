from aiogram import Router
from .handle_first_time import router as start_router
from .handle_quote import router as quote_router
from .handle_help import router as help_router

router = Router(name=__name__)
router.include_router(start_router)
router.include_router(quote_router)
router.include_router(help_router)
