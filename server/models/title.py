import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.models.base import Base


class TitleType(str, enum.Enum):
    PERSONAL = "personal"
    GUILD = "guild"


class TitleVisibility(str, enum.Enum):
    PUBLIC = "public"
    HIDDEN = "hidden"


class Title(Base):
    __tablename__ = "titles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[TitleType] = mapped_column(Enum(TitleType), nullable=False)
    visibility: Mapped[TitleVisibility] = mapped_column(
        Enum(TitleVisibility), nullable=False, default=TitleVisibility.PUBLIC
    )
    condition: Mapped[str] = mapped_column(Text, nullable=False)
    theme_color: Mapped[str] = mapped_column(String(32), nullable=False, default="#b34c24")
    active_start_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    active_end_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    users: Mapped[list["UserTitle"]] = relationship(back_populates="title")


class UserTitle(Base):
    __tablename__ = "user_titles"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    title_id: Mapped[int] = mapped_column(ForeignKey("titles.id"), primary_key=True)
    earned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="titles")
    title: Mapped["Title"] = relationship(back_populates="users")
