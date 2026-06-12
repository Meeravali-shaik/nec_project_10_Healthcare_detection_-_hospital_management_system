from datetime import date, time

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.models.appointment import Appointment, AppointmentStatus
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate


ACTIVE_STATUSES = {AppointmentStatus.pending, AppointmentStatus.approved}


def list_appointments(db: Session, patient_id: int | None = None, doctor_id: int | None = None) -> list[Appointment]:
    stmt = select(Appointment).order_by(Appointment.appointment_date.desc(), Appointment.appointment_time.desc())
    if patient_id is not None:
        stmt = stmt.where(Appointment.patient_id == patient_id)
    if doctor_id is not None:
        stmt = stmt.where(Appointment.doctor_id == doctor_id)
    return list(db.scalars(stmt).all())


def get_appointment(db: Session, appointment_id: int) -> Appointment | None:
    return db.get(Appointment, appointment_id)


def _slot_taken(db: Session, doctor_id: int, appointment_date: date, appointment_time: time, exclude_id: int | None = None) -> bool:
    stmt = select(Appointment).where(
        and_(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date == appointment_date,
            Appointment.appointment_time == appointment_time,
            Appointment.appointment_status.in_(ACTIVE_STATUSES),
        )
    )
    if exclude_id is not None:
        stmt = stmt.where(Appointment.appointment_id != exclude_id)
    return db.scalar(stmt) is not None


def create_appointment(db: Session, payload: AppointmentCreate) -> Appointment:
    if payload.patient_id is None:
        raise AppError("patient_id is required for staff/admin bookings.", 400)
    if _slot_taken(db, payload.doctor_id, payload.appointment_date, payload.appointment_time):
        raise AppError("Selected slot is already booked.", 409)
    appointment = Appointment(
        patient_id=payload.patient_id,
        doctor_id=payload.doctor_id,
        appointment_date=payload.appointment_date,
        appointment_time=payload.appointment_time,
        notes=payload.notes,
        appointment_status=AppointmentStatus.pending,
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment


def update_appointment(db: Session, appointment: Appointment, payload: AppointmentUpdate) -> Appointment:
    update_data = payload.model_dump(exclude_unset=True)
    new_date = update_data.get("appointment_date", appointment.appointment_date)
    new_time = update_data.get("appointment_time", appointment.appointment_time)
    if _slot_taken(db, appointment.doctor_id, new_date, new_time, exclude_id=appointment.appointment_id):
        raise AppError("Selected slot is already booked.", 409)
    for key, value in update_data.items():
        setattr(appointment, key, value)
    db.commit()
    db.refresh(appointment)
    return appointment


def change_status(db: Session, appointment: Appointment, status: AppointmentStatus) -> Appointment:
    appointment.appointment_status = status
    db.commit()
    db.refresh(appointment)
    return appointment


def delete_appointment(db: Session, appointment: Appointment) -> None:
    db.delete(appointment)
    db.commit()
