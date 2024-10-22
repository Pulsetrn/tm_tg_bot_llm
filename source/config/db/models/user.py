from sqlalchemy.orm import Mapped, relationship
from typing import TYPE_CHECKING
from source.config.db.models.base import Base

if TYPE_CHECKING:
    from source.config.db.models.deck import Deck
    from source.config.db.models.comlpeted_task import Completed_task
    from source.config.db.models.profile import Profile
    from source.config.db.models.task import Task


class User(Base):
    completed_tasks: Mapped[list["Completed_task"]] = relationship(
        back_populates="user"
    )
    tasks: Mapped[list["Task"]] = relationship(back_populates="user")
    decks: Mapped[list["Deck"]] = relationship(back_populates="user")
    profile: Mapped["Profile"] = relationship(back_populates="user")
    fullname: Mapped[str]
    range_of_interests: Mapped[str | None]
