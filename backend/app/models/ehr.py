from datetime import date, datetime, timezone
from enum import Enum

from sqlalchemy import Date, DateTime, Enum as SQLEnum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ReportType(str, Enum):
    blood_test = "Blood Test"
    urine_test = "Urine Test"
    ecg = "ECG"
    mri = "MRI"
    ct_scan = "CT Scan"
    x_ray = "X-Ray"
    other = "Other"


class SeverityLevel(str, Enum):
    mild = "Mild"
    moderate = "Moderate"
    severe = "Severe"


class MedicalRecord(Base):
    __tablename__ = "medical_records"

    record_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.patient_id"), nullable=False, index=True)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.doctor_id"), nullable=False, index=True)
    visit_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    chief_complaint: Mapped[str | None] = mapped_column(String(255), nullable=True)
    diagnosis: Mapped[str | None] = mapped_column(Text, nullable=True)
    symptoms: Mapped[str | None] = mapped_column(Text, nullable=True)
    treatment_plan: Mapped[str | None] = mapped_column(Text, nullable=True)
    follow_up_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    patient = relationship("Patient", back_populates="medical_records")
    doctor = relationship("Doctor", back_populates="medical_records")


class Prescription(Base):
    __tablename__ = "prescriptions"

    prescription_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.patient_id"), nullable=False, index=True)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.doctor_id"), nullable=False, index=True)
    issue_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    dosage: Mapped[str | None] = mapped_column(Text, nullable=True)
    frequency: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration: Mapped[str | None] = mapped_column(Text, nullable=True)
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    patient = relationship("Patient", back_populates="prescriptions")
    doctor = relationship("Doctor", back_populates="prescriptions")
    medications = relationship("Medication", back_populates="prescription", cascade="all, delete-orphan")


class Medication(Base):
    __tablename__ = "medications"

    medication_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    prescription_id: Mapped[int] = mapped_column(ForeignKey("prescriptions.prescription_id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    dosage: Mapped[str | None] = mapped_column(String(100), nullable=True)
    frequency: Mapped[str | None] = mapped_column(String(100), nullable=True)
    duration: Mapped[str | None] = mapped_column(String(100), nullable=True)
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True)

    prescription = relationship("Prescription", back_populates="medications")


class LabReport(Base):
    __tablename__ = "lab_reports"

    report_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.patient_id"), nullable=False, index=True)
    uploaded_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    report_type: Mapped[ReportType] = mapped_column(SQLEnum(ReportType), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    upload_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    patient = relationship("Patient", back_populates="lab_reports")
    uploader = relationship("User")


class TreatmentHistory(Base):
    __tablename__ = "treatment_histories"

    treatment_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.patient_id"), nullable=False, index=True)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.doctor_id"), nullable=False, index=True)
    treatment_name: Mapped[str] = mapped_column(String(255), nullable=False)
    diagnosis: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    outcome: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    patient = relationship("Patient", back_populates="treatments")
    doctor = relationship("Doctor", back_populates="treatments")


class Vaccination(Base):
    __tablename__ = "vaccinations"

    vaccination_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.patient_id"), nullable=False, index=True)
    vaccine_name: Mapped[str] = mapped_column(String(255), nullable=False)
    dose_number: Mapped[int] = mapped_column(Integer, nullable=False)
    vaccination_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    next_due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    patient = relationship("Patient", back_populates="vaccinations")


class Allergy(Base):
    __tablename__ = "allergies"

    allergy_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.patient_id"), nullable=False, index=True)
    allergy_name: Mapped[str] = mapped_column(String(255), nullable=False)
    severity: Mapped[SeverityLevel] = mapped_column(SQLEnum(SeverityLevel), nullable=False)
    reaction: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    patient = relationship("Patient", back_populates="allergies")

