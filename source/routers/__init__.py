from aiogram import Router
from .survey import router as survey_router

router = Router(name=__name__)
router.include_router(survey_router)
