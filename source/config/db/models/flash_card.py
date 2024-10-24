import datetime
from enum import Enum
from sqlalchemy import DateTime, func
from source.config.db.models.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey

if TYPE_CHECKING:
    from source.config.db.models.deck import Deck


# class Level(Enum):
#     PENDING = "pending"
#     BAD = "bad"
#     MEDIUM = "medium"
#     GOOD = "good"


class Flash_card(Base):
    deck_id: Mapped[int] = mapped_column(ForeignKey("decks.id"), unique=False)
    question: Mapped[str] = mapped_column(unique=True)
    answer: Mapped[str]
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now())
    deck: Mapped["Deck"] = relationship(back_populates="cards")
    # TODO: придумать алгоритм с пониманием пользователя
    # level_of_understanding: Mapped[Level] = mapped_column(default=Level.PENDING)
