from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.models.patient import Patient
from app.schemas.patient import PatientCreate, PatientUpdate


def list_patients(db: Session, search: str | None = None) -> list[Patient]:
    stmt = select(Patient).order_by(Patient.patient_id.desc())
    if search:
        like = f"%{search}%"
        stmt = stmt.where(
            or_(
                Patient.full_name.ilike(like),
                Patient.blood_group.ilike(like),
                Patient.emergency_contact.ilike(like),
            )
        )
    return list(db.scalars(stmt).all())


def get_patient(db: Session, patient_id: int) -> Patient | None:
    return db.get(Patient, patient_id)


def create_patient(db: Session, payload: PatientCreate) -> Patient:
    patient = Patient(**payload.model_dump())
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


def update_patient(db: Session, patient: Patient, payload: PatientUpdate) -> Patient:
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(patient, key, value)
    db.commit()
    db.refresh(patient)
    return patient


def delete_patient(db: Session, patient: Patient) -> None:
    db.delete(patient)
    db.commit()

