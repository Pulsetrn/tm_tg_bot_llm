from source.config.db.helpers.usermixin import UserRelationMixin
from source.config.db.models.base import Base
from sqlalchemy.orm import Mapped, mapped_column


class Profile(Base, UserRelationMixin):
    _user_back_populates = "profile"
    _user_id_unique_flag = True
    tg_id: Mapped[int] = mapped_column(unique=True)
    email: Mapped[str | None] = mapped_column(unique=True)
    bio: Mapped[str | None]