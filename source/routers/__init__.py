from aiogram import Router
from .profile_survey import router as survey_router
from .commands import router as main_commands_router
from .llm_qna import router as llm_router

router = Router(name=__name__)
router.include_router(survey_router)
router.include_router(main_commands_router)


# ВСЕГДА ПОСЛЕДНИМ
router.include_router(llm_router)
