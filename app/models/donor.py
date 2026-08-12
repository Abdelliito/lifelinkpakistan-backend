import uuid
from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import BloodGroup, City, DonorAvailability


class Donor(Base):
    __tablename__ = "donors"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: f"d_{uuid.uuid4().hex[:10]}")
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    initials: Mapped[str] = mapped_column(String(4), nullable=False)
    blood_group: Mapped[BloodGroup] = mapped_column(Enum(BloodGroup), nullable=False)
    city: Mapped[City] = mapped_column(Enum(City), nullable=False)
    availability: Mapped[DonorAvailability] = mapped_column(
        Enum(DonorAvailability), default=DonorAvailability.AVAILABLE, nullable=False
    )
    phone: Mapped[str] = mapped_column(String(30), nullable=False)
    last_donation_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    joined_date: Mapped[date] = mapped_column(Date, default=lambda: datetime.now(timezone.utc).date())

    user: Mapped["User"] = relationship(back_populates="donor_profile")
