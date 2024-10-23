from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import types
from source.config.db.models.profile import Profile
from sqlalchemy import select
from sqlalchemy.orm import joinedload
