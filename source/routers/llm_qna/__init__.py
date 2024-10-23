from aiogram import Router
from .handlers import router as llm_router

router = Router(name=__name__)
router.include_router(llm_router)
