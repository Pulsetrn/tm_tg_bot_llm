from sqlalchemy.orm import declared_attr, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from source.config.db.models.user import User


class UserRelationMixin:
    _user_id_nullable_flag: bool = False
    _user_id_unique_flag: bool = False
    _user_back_populates: str | None = None

    @declared_attr
    def user_id(cls) -> Mapped[int]:
        return mapped_column(
            ForeignKey("users.id"),
            unique=cls._user_id_unique_flag,
            nullable=cls._user_id_nullable_flag,
        )

    @declared_attr
    def user(cls) -> Mapped["User"]:
        return relationship(
            "User",
            back_populates=cls._user_back_populates,
        )
