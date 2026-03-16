from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.models.base import Base


class Character(Base):
    __tablename__ = "characters"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    character_class: Mapped[str] = mapped_column(
        "class", String(50), nullable=False, default="Novice"
    )
    level: Mapped[int] = mapped_column(default=1, nullable=False)
    exp: Mapped[int] = mapped_column(default=0, nullable=False)
    impl: Mapped[int] = mapped_column(default=0, nullable=False)
    focus: Mapped[int] = mapped_column(default=0, nullable=False)
    efficiency: Mapped[int] = mapped_column(default=0, nullable=False)
    versatility: Mapped[int] = mapped_column(default=0, nullable=False)
    stability: Mapped[int] = mapped_column(default=0, nullable=False)
    endurance: Mapped[int] = mapped_column(default=0, nullable=False)
    title: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user: Mapped["User"] = relationship(back_populates="character")

