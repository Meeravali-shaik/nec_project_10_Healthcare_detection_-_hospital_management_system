from datetime import date

from sqlalchemy import Date, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Patient(Base):
    __tablename__ = "patients"

    patient_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), unique=True, nullable=True)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    gender: Mapped[str | None] = mapped_column(String(20), nullable=True)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    blood_group: Mapped[str | None] = mapped_column(String(10), nullable=True)
    weight: Mapped[float | None] = mapped_column(Float, nullable=True)
    height: Mapped[float | None] = mapped_column(Float, nullable=True)
    allergies: Mapped[str | None] = mapped_column(Text, nullable=True)
    medical_history: Mapped[str | None] = mapped_column(Text, nullable=True)
    family_history: Mapped[str | None] = mapped_column(Text, nullable=True)
    emergency_contact: Mapped[str | None] = mapped_column(String(100), nullable=True)
    insurance_provider: Mapped[str | None] = mapped_column(String(150), nullable=True)
    insurance_number: Mapped[str | None] = mapped_column(String(150), nullable=True)

    user = relationship("User", back_populates="patient_profile")
    appointments = relationship("Appointment", back_populates="patient", cascade="all, delete-orphan")
    medical_records = relationship("MedicalRecord", back_populates="patient", cascade="all, delete-orphan")
    prescriptions = relationship("Prescription", back_populates="patient", cascade="all, delete-orphan")
    lab_reports = relationship("LabReport", back_populates="patient", cascade="all, delete-orphan")
    treatments = relationship("TreatmentHistory", back_populates="patient", cascade="all, delete-orphan")
    vaccinations = relationship("Vaccination", back_populates="patient", cascade="all, delete-orphan")
    allergies = relationship("Allergy", back_populates="patient", cascade="all, delete-orphan")
