import uuid
from datetime import date, datetime, timezone

from sqlalchemy import Boolean, Date, DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import UserRole, UserStatus


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: f"u_{uuid.uuid4().hex[:10]}")
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.USER, nullable=False)
    status: Mapped[UserStatus] = mapped_column(Enum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    is_donor: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    join_date: Mapped[date] = mapped_column(Date, default=lambda: datetime.now(timezone.utc).date())
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    donor_profile: Mapped["Donor | None"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    blood_requests: Mapped[list["BloodRequest"]] = relationship(back_populates="user", cascade="all, delete-orphan")
