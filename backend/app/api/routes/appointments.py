from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db, require_roles
from app.models.appointment import Appointment, AppointmentStatus
from app.models.user import User, UserRole
from app.schemas.appointment import AppointmentCreate, AppointmentRead, AppointmentStatusUpdate, AppointmentUpdate
from app.services.appointment_service import change_status, create_appointment, get_appointment, list_appointments, update_appointment

router = APIRouter()


@router.get("/", response_model=list[AppointmentRead])
def read_appointments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Appointment]:
    if current_user.role == UserRole.patient:
        if not current_user.patient_profile:
            raise HTTPException(status_code=403, detail="Patient profile not found")
        return list_appointments(db, patient_id=current_user.patient_profile.patient_id)
    if current_user.role == UserRole.doctor:
        if not current_user.doctor_profile:
            raise HTTPException(status_code=403, detail="Doctor profile not found")
        return list_appointments(db, doctor_id=current_user.doctor_profile.doctor_id)
    return list_appointments(db)


@router.post("/", response_model=AppointmentRead, status_code=status.HTTP_201_CREATED)
def book_appointment(payload: AppointmentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Appointment:
    if current_user.role == UserRole.patient and current_user.patient_profile:
        payload.patient_id = current_user.patient_profile.patient_id
    elif current_user.role not in {UserRole.admin, UserRole.staff}:
        raise HTTPException(status_code=403, detail="Only patients, staff, or admins can create appointments")
    return create_appointment(db, payload)


@router.put("/{appointment_id}", response_model=AppointmentRead)
def reschedule_appointment(
    appointment_id: int,
    payload: AppointmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Appointment:
    appointment = get_appointment(db, appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if current_user.role == UserRole.patient and (not current_user.patient_profile or appointment.patient_id != current_user.patient_profile.patient_id):
        raise HTTPException(status_code=403, detail="Access denied")
    return update_appointment(db, appointment, payload)


@router.patch("/{appointment_id}/status", response_model=AppointmentRead, dependencies=[Depends(require_roles(UserRole.doctor, UserRole.admin, UserRole.staff))])
def update_status(
    appointment_id: int,
    payload: AppointmentStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Appointment:
    appointment = get_appointment(db, appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if current_user.role == UserRole.doctor:
        if not current_user.doctor_profile:
            raise HTTPException(status_code=403, detail="Doctor profile not found")
        if appointment.doctor_id != current_user.doctor_profile.doctor_id:
            raise HTTPException(status_code=403, detail="Access denied")
    return change_status(db, appointment, payload.appointment_status)


@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    appointment = get_appointment(db, appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if current_user.role == UserRole.patient:
        if not current_user.patient_profile or appointment.patient_id != current_user.patient_profile.patient_id:
            raise HTTPException(status_code=403, detail="Access denied")
    elif current_user.role not in {UserRole.admin, UserRole.staff}:
        raise HTTPException(status_code=403, detail="Access denied")
    appointment.appointment_status = AppointmentStatus.cancelled
    db.commit()
    db.refresh(appointment)
