from datetime import date

from app.schemas.common import ORMBaseModel


class PatientBase(ORMBaseModel):
    full_name: str
    age: int | None = None
    gender: str | None = None
    date_of_birth: date | None = None
    blood_group: str | None = None
    weight: float | None = None
    height: float | None = None
    allergies: str | None = None
    medical_history: str | None = None
    family_history: str | None = None
    emergency_contact: str | None = None
    insurance_provider: str | None = None
    insurance_number: str | None = None


class PatientCreate(PatientBase):
    user_id: int | None = None


class PatientUpdate(PatientBase):
    full_name: str | None = None
    age: int | None = None
    gender: str | None = None
    date_of_birth: date | None = None
    blood_group: str | None = None
    weight: float | None = None
    height: float | None = None
    allergies: str | None = None
    medical_history: str | None = None
    family_history: str | None = None
    emergency_contact: str | None = None
    insurance_provider: str | None = None
    insurance_number: str | None = None


class PatientRead(PatientBase):
    patient_id: int
    user_id: int | None = None
