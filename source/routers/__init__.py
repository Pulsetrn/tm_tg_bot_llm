from aiogram import Router
from .survey import router as survey_router
from .handle_first_time import router as first_time_router

router = Router(name=__name__)
router.include_router(survey_router)
router.include_router(first_time_router)
