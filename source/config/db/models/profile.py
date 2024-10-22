from source.config.db.helpers.usermixin import UserRelationMixin
from source.config.db.models.base import Base
from sqlalchemy.orm import Mapped, mapped_column


class Profile(Base, UserRelationMixin):
    _user_back_populates = "profile"
    _user_id_unique_flag = True
    range_of_interests: Mapped[str | None]
    email: Mapped[str | None] = mapped_column(unique=True)
    bio: Mapped[str | None]
