import datetime

from sqlalchemy import DateTime, func
from source.config.db.helpers.usermixin import UserRelationMixin
from source.config.db.models.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from source.config.db.models.flash_card import Flash_card


class Deck(Base, UserRelationMixin):
    _user_back_populates = "decks"
    cards: Mapped[list["Flash_card"]] = relationship(back_populates="deck")
    name: Mapped[str]
    tag: Mapped[str | None]
    recent_interaction: Mapped[datetime.date | None]
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now())