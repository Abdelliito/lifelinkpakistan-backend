import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import BloodGroup, City, RequestStatus, UrgencyLevel


class BloodRequest(Base):
    __tablename__ = "blood_requests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: f"r_{uuid.uuid4().hex[:10]}")
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    patient_name: Mapped[str] = mapped_column(String(120), nullable=False)
    blood_group: Mapped[BloodGroup] = mapped_column(Enum(BloodGroup), nullable=False)
    hospital: Mapped[str] = mapped_column(String(160), nullable=False)
    city: Mapped[City] = mapped_column(Enum(City), nullable=False)
    urgency: Mapped[UrgencyLevel] = mapped_column(Enum(UrgencyLevel), nullable=False)
    status: Mapped[RequestStatus] = mapped_column(Enum(RequestStatus), default=RequestStatus.OPEN, nullable=False)
    contact_number: Mapped[str] = mapped_column(String(30), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    user: Mapped["User"] = relationship(back_populates="blood_requests")
