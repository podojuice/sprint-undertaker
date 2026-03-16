import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.models.base import Base


class Provider(str, enum.Enum):
    CLAUDE_CODE = "claude_code"
    # CODEX = "codex"
    # CURSOR = "cursor"
    # AIDER = "aider"


class InstallationStatus(str, enum.Enum):
    ACTIVE = "active"
    DISABLED = "disabled"


class ProviderInstallation(Base):
    __tablename__ = "provider_installations"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    provider: Mapped[Provider] = mapped_column(Enum(Provider), nullable=False)
    installation_name: Mapped[str] = mapped_column(String(255), nullable=False)
    api_key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    status: Mapped[InstallationStatus] = mapped_column(
        Enum(InstallationStatus), default=InstallationStatus.ACTIVE, nullable=False
    )
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="installations")
    events: Mapped[list["ActivityEvent"]] = relationship(
        back_populates="installation", cascade="all, delete-orphan"
    )

