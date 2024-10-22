from source.config.db.helpers.usermixin import UserRelationMixin
from source.config.db.models.base import Base
import datetime
from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


class Task(Base, UserRelationMixin):
    _user_back_populates = "tasks"
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now())
    deadline: Mapped[datetime.datetime | None]
    name: Mapped[str]
    description: Mapped[str]