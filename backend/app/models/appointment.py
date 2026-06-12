from datetime import date, datetime, time, timezone
from enum import Enum

from sqlalchemy import Date, DateTime, Enum as SQLEnum, ForeignKey, Integer, Text, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class AppointmentStatus(str, Enum):
    pending = "Pending"
    approved = "Approved"
    rejected = "Rejected"
    completed = "Completed"
    cancelled = "Cancelled"


class Appointment(Base):
    __tablename__ = "appointments"

    appointment_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.patient_id"), nullable=False, index=True)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.doctor_id"), nullable=False, index=True)
    appointment_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    appointment_time: Mapped[time] = mapped_column(Time, nullable=False, index=True)
    appointment_status: Mapped[AppointmentStatus] = mapped_column(SQLEnum(AppointmentStatus), default=AppointmentStatus.pending, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")
