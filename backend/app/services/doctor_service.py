from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.doctor import Doctor
from app.schemas.doctor import DoctorCreate, DoctorUpdate


def list_doctors(db: Session, search: str | None = None) -> list[Doctor]:
    stmt = select(Doctor).order_by(Doctor.doctor_id.desc())
    if search:
        like = f"%{search}%"
        stmt = stmt.where(
            or_(
                Doctor.full_name.ilike(like),
                Doctor.specialization.ilike(like),
                Doctor.department.ilike(like),
            )
        )
    return list(db.scalars(stmt).all())


def get_doctor(db: Session, doctor_id: int) -> Doctor | None:
    return db.get(Doctor, doctor_id)


def create_doctor(db: Session, payload: DoctorCreate) -> Doctor:
    doctor = Doctor(**payload.model_dump())
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor


def update_doctor(db: Session, doctor: Doctor, payload: DoctorUpdate) -> Doctor:
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(doctor, key, value)
    db.commit()
    db.refresh(doctor)
    return doctor


def delete_doctor(db: Session, doctor: Doctor) -> None:
    db.delete(doctor)
    db.commit()

