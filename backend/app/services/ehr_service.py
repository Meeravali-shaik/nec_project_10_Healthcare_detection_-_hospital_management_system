from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, date
from pathlib import Path
from typing import Iterable
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.models.appointment import Appointment
from app.models.doctor import Doctor
from app.models.ehr import Allergy, LabReport, MedicalRecord, Medication, Prescription, ReportType, SeverityLevel, TreatmentHistory, Vaccination
from app.models.patient import Patient
from app.models.user import User, UserRole
from app.schemas.ehr import (
    AllergyCreate,
    AllergyUpdate,
    LabReportRead,
    MedicalRecordCreate,
    MedicalRecordUpdate,
    MedicationBase,
    PaginationMeta,
    PrescriptionCreate,
    PrescriptionUpdate,
    TimelineEvent,
    TreatmentHistoryCreate,
    TreatmentHistoryUpdate,
    VaccinationCreate,
    VaccinationUpdate,
)


ALLOWED_REPORT_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}


def paginate_query(query, page: int, size: int, db: Session):
    page = max(page, 1)
    size = max(min(size, 100), 1)
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    items = db.scalars(query.offset((page - 1) * size).limit(size)).all()
    pages = max((total + size - 1) // size, 1) if total else 0
    return items, PaginationMeta(page=page, size=size, total=total, pages=pages)


def _ensure_patient_access(current_user: User, patient_id: int) -> None:
    if current_user.role in {UserRole.admin, UserRole.staff}:
        return
    if current_user.role == UserRole.patient and current_user.patient_profile and current_user.patient_profile.patient_id == patient_id:
        return
    if current_user.role == UserRole.doctor:
        return
    raise AppError("Access denied.", 403)


def _ensure_doctor_access(current_user: User, doctor_id: int) -> None:
    if current_user.role in {UserRole.admin, UserRole.staff}:
        return
    if current_user.role == UserRole.doctor and current_user.doctor_profile and current_user.doctor_profile.doctor_id == doctor_id:
        return
    raise AppError("Access denied.", 403)


def _ensure_patient_owns_record(current_user: User, patient_id: int) -> None:
    if current_user.role == UserRole.patient and (not current_user.patient_profile or current_user.patient_profile.patient_id != patient_id):
        raise AppError("Access denied.", 403)


def _serialize_medications(medications: Iterable[Medication]) -> list[dict]:
    return [
        {
            "medication_id": medication.medication_id,
            "name": medication.name,
            "dosage": medication.dosage,
            "frequency": medication.frequency,
            "duration": medication.duration,
            "instructions": medication.instructions,
        }
        for medication in medications
    ]


def _upsert_medications(db: Session, prescription: Prescription, medications: list[MedicationBase] | None) -> None:
    if medications is None:
        return
    prescription.medications.clear()
    db.flush()
    for item in medications:
        prescription.medications.append(
            Medication(
                name=item.name,
                dosage=item.dosage,
                frequency=item.frequency,
                duration=item.duration,
                instructions=item.instructions,
            )
        )


def create_medical_record(db: Session, payload: MedicalRecordCreate, current_user: User) -> MedicalRecord:
    _ensure_patient_access(current_user, payload.patient_id)
    _ensure_doctor_access(current_user, payload.doctor_id)
    record = MedicalRecord(**payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def list_medical_records(db: Session, current_user: User, search: str | None = None, page: int = 1, size: int = 20):
    stmt = select(MedicalRecord).order_by(MedicalRecord.visit_date.desc(), MedicalRecord.record_id.desc())
    if current_user.role == UserRole.patient:
        if not current_user.patient_profile:
            raise AppError("Patient profile not found.", 403)
        stmt = stmt.where(MedicalRecord.patient_id == current_user.patient_profile.patient_id)
    elif current_user.role == UserRole.doctor:
        if not current_user.doctor_profile:
            raise AppError("Doctor profile not found.", 403)
        stmt = stmt.where(MedicalRecord.doctor_id == current_user.doctor_profile.doctor_id)
    if search:
        like = f"%{search}%"
        stmt = stmt.where(or_(MedicalRecord.chief_complaint.ilike(like), MedicalRecord.diagnosis.ilike(like), MedicalRecord.symptoms.ilike(like)))
    return paginate_query(stmt, page, size, db)


def get_medical_record(db: Session, record_id: int) -> MedicalRecord | None:
    return db.get(MedicalRecord, record_id)


def update_medical_record(db: Session, record: MedicalRecord, payload: MedicalRecordUpdate, current_user: User) -> MedicalRecord:
    _ensure_doctor_access(current_user, record.doctor_id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(record, key, value)
    db.commit()
    db.refresh(record)
    return record


def create_prescription(db: Session, payload: PrescriptionCreate, current_user: User) -> Prescription:
    _ensure_patient_access(current_user, payload.patient_id)
    _ensure_doctor_access(current_user, payload.doctor_id)
    prescription = Prescription(
        patient_id=payload.patient_id,
        doctor_id=payload.doctor_id,
        issue_date=payload.issue_date,
        dosage=payload.dosage,
        frequency=payload.frequency,
        duration=payload.duration,
        instructions=payload.instructions,
    )
    db.add(prescription)
    db.flush()
    _upsert_medications(db, prescription, payload.medications)
    db.commit()
    db.refresh(prescription)
    return prescription


def list_prescriptions(db: Session, current_user: User, search: str | None = None, page: int = 1, size: int = 20):
    stmt = select(Prescription).order_by(Prescription.issue_date.desc(), Prescription.prescription_id.desc())
    if current_user.role == UserRole.patient:
        if not current_user.patient_profile:
            raise AppError("Patient profile not found.", 403)
        stmt = stmt.where(Prescription.patient_id == current_user.patient_profile.patient_id)
    elif current_user.role == UserRole.doctor:
        if not current_user.doctor_profile:
            raise AppError("Doctor profile not found.", 403)
        stmt = stmt.where(Prescription.doctor_id == current_user.doctor_profile.doctor_id)
    if search:
        like = f"%{search}%"
        stmt = stmt.join(Prescription.medications, isouter=True).where(or_(Medication.name.ilike(like), Prescription.instructions.ilike(like), Prescription.dosage.ilike(like)))
    return paginate_query(stmt.distinct(), page, size, db)


def get_prescription(db: Session, prescription_id: int) -> Prescription | None:
    return db.get(Prescription, prescription_id)


def update_prescription(db: Session, prescription: Prescription, payload: PrescriptionUpdate, current_user: User) -> Prescription:
    _ensure_doctor_access(current_user, prescription.doctor_id)
    for key, value in payload.model_dump(exclude_unset=True, exclude={"medications"}).items():
        setattr(prescription, key, value)
    _upsert_medications(db, prescription, payload.medications)
    db.commit()
    db.refresh(prescription)
    return prescription


def create_lab_report(db: Session, patient_id: int, current_user: User, upload: UploadFile, report_type: ReportType, description: str | None = None) -> LabReport:
    if current_user.role not in {UserRole.admin, UserRole.staff}:
        raise AppError("Only admins or hospital staff can upload reports.", 403)
    _ensure_patient_access(current_user, patient_id)
    suffix = Path(upload.filename or "").suffix.lower()
    if suffix not in ALLOWED_REPORT_EXTENSIONS:
        raise AppError("Unsupported file type. Use PDF, JPG, JPEG, or PNG.", 400)

    storage_dir = Path("storage") / "reports" / str(patient_id)
    storage_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid4().hex}_{Path(upload.filename).name}"
    file_path = storage_dir / filename
    content = upload.file.read()
    file_path.write_bytes(content)

    report = LabReport(
        patient_id=patient_id,
        uploaded_by=current_user.id,
        report_type=report_type,
        file_name=upload.filename or filename,
        file_path=str(file_path.as_posix()),
        description=description,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def list_lab_reports(db: Session, current_user: User, search: str | None = None, page: int = 1, size: int = 20):
    stmt = select(LabReport).order_by(LabReport.upload_date.desc(), LabReport.report_id.desc())
    if current_user.role == UserRole.patient:
        if not current_user.patient_profile:
            raise AppError("Patient profile not found.", 403)
        stmt = stmt.where(LabReport.patient_id == current_user.patient_profile.patient_id)
    if search:
        like = f"%{search}%"
        stmt = stmt.where(or_(LabReport.file_name.ilike(like), LabReport.description.ilike(like)))
    return paginate_query(stmt, page, size, db)


def get_lab_report(db: Session, report_id: int) -> LabReport | None:
    return db.get(LabReport, report_id)


def create_treatment(db: Session, payload: TreatmentHistoryCreate, current_user: User) -> TreatmentHistory:
    _ensure_patient_access(current_user, payload.patient_id)
    _ensure_doctor_access(current_user, payload.doctor_id)
    treatment = TreatmentHistory(**payload.model_dump())
    db.add(treatment)
    db.commit()
    db.refresh(treatment)
    return treatment


def list_treatments(db: Session, current_user: User, search: str | None = None, page: int = 1, size: int = 20):
    stmt = select(TreatmentHistory).order_by(TreatmentHistory.start_date.desc(), TreatmentHistory.treatment_id.desc())
    if current_user.role == UserRole.patient:
        if not current_user.patient_profile:
            raise AppError("Patient profile not found.", 403)
        stmt = stmt.where(TreatmentHistory.patient_id == current_user.patient_profile.patient_id)
    elif current_user.role == UserRole.doctor:
        if not current_user.doctor_profile:
            raise AppError("Doctor profile not found.", 403)
        stmt = stmt.where(TreatmentHistory.doctor_id == current_user.doctor_profile.doctor_id)
    if search:
        like = f"%{search}%"
        stmt = stmt.where(or_(TreatmentHistory.treatment_name.ilike(like), TreatmentHistory.diagnosis.ilike(like), TreatmentHistory.outcome.ilike(like)))
    return paginate_query(stmt, page, size, db)


def update_treatment(db: Session, treatment: TreatmentHistory, payload: TreatmentHistoryUpdate, current_user: User) -> TreatmentHistory:
    _ensure_doctor_access(current_user, treatment.doctor_id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(treatment, key, value)
    db.commit()
    db.refresh(treatment)
    return treatment


def create_vaccination(db: Session, payload: VaccinationCreate, current_user: User) -> Vaccination:
    _ensure_patient_access(current_user, payload.patient_id)
    vaccination = Vaccination(**payload.model_dump())
    db.add(vaccination)
    db.commit()
    db.refresh(vaccination)
    return vaccination


def list_vaccinations(db: Session, current_user: User, search: str | None = None, page: int = 1, size: int = 20):
    stmt = select(Vaccination).order_by(Vaccination.vaccination_date.desc(), Vaccination.vaccination_id.desc())
    if current_user.role == UserRole.patient:
        if not current_user.patient_profile:
            raise AppError("Patient profile not found.", 403)
        stmt = stmt.where(Vaccination.patient_id == current_user.patient_profile.patient_id)
    if search:
        like = f"%{search}%"
        stmt = stmt.where(or_(Vaccination.vaccine_name.ilike(like), Vaccination.remarks.ilike(like)))
    return paginate_query(stmt, page, size, db)


def update_vaccination(db: Session, vaccination: Vaccination, payload: VaccinationUpdate, current_user: User) -> Vaccination:
    _ensure_patient_access(current_user, vaccination.patient_id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(vaccination, key, value)
    db.commit()
    db.refresh(vaccination)
    return vaccination


def create_allergy(db: Session, payload: AllergyCreate, current_user: User) -> Allergy:
    _ensure_patient_access(current_user, payload.patient_id)
    allergy = Allergy(**payload.model_dump())
    db.add(allergy)
    db.commit()
    db.refresh(allergy)
    return allergy


def list_allergies(db: Session, current_user: User, search: str | None = None, page: int = 1, size: int = 20):
    stmt = select(Allergy).order_by(Allergy.created_at.desc(), Allergy.allergy_id.desc())
    if current_user.role == UserRole.patient:
        if not current_user.patient_profile:
            raise AppError("Patient profile not found.", 403)
        stmt = stmt.where(Allergy.patient_id == current_user.patient_profile.patient_id)
    if search:
        like = f"%{search}%"
        stmt = stmt.where(or_(Allergy.allergy_name.ilike(like), Allergy.reaction.ilike(like), Allergy.notes.ilike(like)))
    return paginate_query(stmt, page, size, db)


def update_allergy(db: Session, allergy: Allergy, payload: AllergyUpdate, current_user: User) -> Allergy:
    _ensure_patient_access(current_user, allergy.patient_id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(allergy, key, value)
    db.commit()
    db.refresh(allergy)
    return allergy


def build_patient_timeline(db: Session, patient_id: int, current_user: User) -> list[TimelineEvent]:
    _ensure_patient_owns_record(current_user, patient_id)
    if current_user.role == UserRole.patient and current_user.patient_profile and current_user.patient_profile.patient_id != patient_id:
        raise AppError("Access denied.", 403)

    events: list[TimelineEvent] = []

    appointments = db.scalars(select(Appointment).where(Appointment.patient_id == patient_id)).all()
    for item in appointments:
        events.append(TimelineEvent(event_date=item.appointment_date, event_type="Appointment", title=f"Appointment with doctor #{item.doctor_id}", description=item.notes, source_id=item.appointment_id))

    medical_records = db.scalars(select(MedicalRecord).where(MedicalRecord.patient_id == patient_id)).all()
    for item in medical_records:
        events.append(TimelineEvent(event_date=item.visit_date, event_type="Diagnosis", title=item.chief_complaint or "Medical record", description=item.diagnosis, source_id=item.record_id))

    prescriptions = db.scalars(select(Prescription).where(Prescription.patient_id == patient_id)).all()
    for item in prescriptions:
        events.append(TimelineEvent(event_date=item.issue_date, event_type="Prescription", title=f"Prescription #{item.prescription_id}", description=item.instructions, source_id=item.prescription_id))

    reports = db.scalars(select(LabReport).where(LabReport.patient_id == patient_id)).all()
    for item in reports:
        events.append(TimelineEvent(event_date=item.upload_date.date(), event_type="Report", title=item.report_type.value, description=item.description, source_id=item.report_id))

    treatments = db.scalars(select(TreatmentHistory).where(TreatmentHistory.patient_id == patient_id)).all()
    for item in treatments:
        events.append(TimelineEvent(event_date=item.start_date, event_type="Treatment", title=item.treatment_name, description=item.outcome, source_id=item.treatment_id))

    vaccinations = db.scalars(select(Vaccination).where(Vaccination.patient_id == patient_id)).all()
    for item in vaccinations:
        events.append(TimelineEvent(event_date=item.vaccination_date, event_type="Vaccination", title=item.vaccine_name, description=item.remarks, source_id=item.vaccination_id))

    events.sort(key=lambda event: (event.event_date, event.event_type))
    return events


def build_my_timeline(db: Session, current_user: User) -> list[TimelineEvent]:
    if current_user.role != UserRole.patient or not current_user.patient_profile:
        raise AppError("Patient profile not found.", 403)
    return build_patient_timeline(db, current_user.patient_profile.patient_id, current_user)


def serialize_prescription(prescription: Prescription) -> dict:
    return {
        "prescription_id": prescription.prescription_id,
        "patient_id": prescription.patient_id,
        "doctor_id": prescription.doctor_id,
        "issue_date": prescription.issue_date,
        "dosage": prescription.dosage,
        "frequency": prescription.frequency,
        "duration": prescription.duration,
        "instructions": prescription.instructions,
        "medications": _serialize_medications(prescription.medications),
        "created_at": prescription.created_at,
    }


def serialize_lab_report(report: LabReport) -> dict:
    return {
        "report_id": report.report_id,
        "patient_id": report.patient_id,
        "uploaded_by": report.uploaded_by,
        "report_type": report.report_type,
        "file_name": report.file_name,
        "file_path": report.file_path,
        "upload_date": report.upload_date,
        "description": report.description,
        "created_at": report.created_at,
    }
