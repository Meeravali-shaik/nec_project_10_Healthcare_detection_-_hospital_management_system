from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Doctor(Base):
    __tablename__ = "doctors"

    doctor_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), unique=True, nullable=True)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    specialization: Mapped[str | None] = mapped_column(String(150), nullable=True)
    department: Mapped[str | None] = mapped_column(String(150), nullable=True)
    qualification: Mapped[str | None] = mapped_column(String(255), nullable=True)
    experience_years: Mapped[int | None] = mapped_column(Integer, nullable=True)
    consultation_fee: Mapped[float | None] = mapped_column(Float, nullable=True)
    phone_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    availability_status: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    user = relationship("User", back_populates="doctor_profile")
    appointments = relationship("Appointment", back_populates="doctor", cascade="all, delete-orphan")
    medical_records = relationship("MedicalRecord", back_populates="doctor", cascade="all, delete-orphan")
    prescriptions = relationship("Prescription", back_populates="doctor", cascade="all, delete-orphan")
    treatments = relationship("TreatmentHistory", back_populates="doctor", cascade="all, delete-orphan")
