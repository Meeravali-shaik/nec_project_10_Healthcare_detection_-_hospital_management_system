from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db, require_roles
from app.models.doctor import Doctor
from app.models.user import User, UserRole
from app.schemas.doctor import DoctorCreate, DoctorRead, DoctorUpdate
from app.services.doctor_service import create_doctor, delete_doctor, get_doctor, list_doctors, update_doctor

router = APIRouter()


@router.get("/", response_model=list[DoctorRead])
def read_doctors(search: str | None = Query(default=None), db: Session = Depends(get_db)) -> list[Doctor]:
    return list_doctors(db, search)


@router.post("/", response_model=DoctorRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles(UserRole.admin, UserRole.staff))])
def create_doctor_endpoint(payload: DoctorCreate, db: Session = Depends(get_db)) -> Doctor:
    return create_doctor(db, payload)


@router.get("/{doctor_id}", response_model=DoctorRead)
def read_doctor(doctor_id: int, db: Session = Depends(get_db)) -> Doctor:
    doctor = get_doctor(db, doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor


@router.put("/{doctor_id}", response_model=DoctorRead, dependencies=[Depends(require_roles(UserRole.admin, UserRole.staff))])
def update_doctor_endpoint(doctor_id: int, payload: DoctorUpdate, db: Session = Depends(get_db)) -> Doctor:
    doctor = get_doctor(db, doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return update_doctor(db, doctor, payload)


@router.delete("/{doctor_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_roles(UserRole.admin, UserRole.staff))])
def delete_doctor_endpoint(doctor_id: int, db: Session = Depends(get_db)) -> None:
    doctor = get_doctor(db, doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    delete_doctor(db, doctor)


@router.get("/me/dashboard")
def doctor_dashboard(current_user: User = Depends(require_roles(UserRole.doctor))) -> dict[str, str]:
    return {"message": f"Welcome, Dr. {current_user.full_name}"}

