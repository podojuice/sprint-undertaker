import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.models.base import Base


class OrgRole(str, enum.Enum):
    OWNER = "owner"
    MEMBER = "member"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    organization_id: Mapped[int | None] = mapped_column(
        ForeignKey("organizations.id"), nullable=True
    )
    org_role: Mapped[OrgRole | None] = mapped_column(Enum(OrgRole), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    character: Mapped["Character"] = relationship(back_populates="user", uselist=False)
    installations: Mapped[list["ProviderInstallation"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    titles: Mapped[list["UserTitle"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    organization: Mapped["Organization | None"] = relationship(
        foreign_keys=[organization_id], back_populates="members"
    )

