from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db, require_roles
from app.models.patient import Patient
from app.models.user import User, UserRole
from app.schemas.patient import PatientCreate, PatientRead, PatientUpdate
from app.services.patient_service import create_patient, delete_patient, get_patient, list_patients, update_patient

router = APIRouter()


@router.get("/", response_model=list[PatientRead], dependencies=[Depends(require_roles(UserRole.admin, UserRole.staff, UserRole.doctor))])
def read_patients(search: str | None = Query(default=None), db: Session = Depends(get_db)) -> list[Patient]:
    return list_patients(db, search)


@router.post("/", response_model=PatientRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles(UserRole.admin, UserRole.staff))])
def create_patient_endpoint(payload: PatientCreate, db: Session = Depends(get_db)) -> Patient:
    return create_patient(db, payload)


@router.get("/{patient_id}", response_model=PatientRead, dependencies=[Depends(require_roles(UserRole.admin, UserRole.staff, UserRole.doctor, UserRole.patient))])
def read_patient(patient_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Patient:
    patient = get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    if current_user.role == UserRole.patient and patient.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return patient


@router.put("/{patient_id}", response_model=PatientRead, dependencies=[Depends(require_roles(UserRole.admin, UserRole.staff))])
def update_patient_endpoint(patient_id: int, payload: PatientUpdate, db: Session = Depends(get_db)) -> Patient:
    patient = get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return update_patient(db, patient, payload)


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_roles(UserRole.admin, UserRole.staff))])
def delete_patient_endpoint(patient_id: int, db: Session = Depends(get_db)) -> None:
    patient = get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    delete_patient(db, patient)

