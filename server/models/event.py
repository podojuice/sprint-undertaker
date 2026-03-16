from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.models.base import Base
from server.models.installation import Provider


class ActivityEvent(Base):
    __tablename__ = "activity_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    installation_id: Mapped[int] = mapped_column(
        ForeignKey("provider_installations.id"), nullable=False
    )
    provider: Mapped[Provider] = mapped_column(nullable=False)
    session_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    canonical_event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    installation: Mapped["ProviderInstallation"] = relationship(back_populates="events")

