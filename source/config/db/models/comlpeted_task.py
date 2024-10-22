from source.config.db.helpers.usermixin import UserRelationMixin
from source.config.db.models.base import Base
import datetime
from sqlalchemy.orm import Mapped


class Completed_task(Base, UserRelationMixin):
    _user_back_populates = "completed_tasks"
    created_at: Mapped[datetime.datetime]
    name: Mapped[str]
    description: Mapped[str]