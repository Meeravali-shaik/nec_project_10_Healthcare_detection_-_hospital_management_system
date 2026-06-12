from datetime import date, datetime

from pydantic import Field

from app.models.ehr import ReportType, SeverityLevel
from app.schemas.common import ORMBaseModel


class PaginationParams(ORMBaseModel):
    page: int = 1
    size: int = 20


class PaginationMeta(ORMBaseModel):
    page: int
    size: int
    total: int
    pages: int


class PaginatedResponse(ORMBaseModel):
    items: list[dict]
    meta: PaginationMeta


class MedicalRecordBase(ORMBaseModel):
    patient_id: int
    doctor_id: int
    visit_date: date
    chief_complaint: str | None = None
    diagnosis: str | None = None
    symptoms: str | None = None
    treatment_plan: str | None = None
    follow_up_date: date | None = None
    notes: str | None = None


class MedicalRecordCreate(MedicalRecordBase):
    pass


class MedicalRecordUpdate(ORMBaseModel):
    visit_date: date | None = None
    chief_complaint: str | None = None
    diagnosis: str | None = None
    symptoms: str | None = None
    treatment_plan: str | None = None
    follow_up_date: date | None = None
    notes: str | None = None


class MedicalRecordRead(MedicalRecordBase):
    record_id: int
    created_at: datetime
    updated_at: datetime


class MedicationBase(ORMBaseModel):
    name: str
    dosage: str | None = None
    frequency: str | None = None
    duration: str | None = None
    instructions: str | None = None


class MedicationRead(MedicationBase):
    medication_id: int


class PrescriptionBase(ORMBaseModel):
    patient_id: int
    doctor_id: int
    issue_date: date
    dosage: str | None = None
    frequency: str | None = None
    duration: str | None = None
    instructions: str | None = None
    medications: list[MedicationBase] = Field(default_factory=list)


class PrescriptionCreate(PrescriptionBase):
    pass


class PrescriptionUpdate(ORMBaseModel):
    issue_date: date | None = None
    dosage: str | None = None
    frequency: str | None = None
    duration: str | None = None
    instructions: str | None = None
    medications: list[MedicationBase] | None = None


class PrescriptionRead(PrescriptionBase):
    prescription_id: int
    created_at: datetime
    medications: list[MedicationRead] = Field(default_factory=list)


class LabReportBase(ORMBaseModel):
    patient_id: int
    report_type: ReportType
    description: str | None = None


class LabReportRead(LabReportBase):
    report_id: int
    uploaded_by: int
    file_name: str
    file_path: str
    upload_date: datetime
    created_at: datetime


class TreatmentHistoryBase(ORMBaseModel):
    patient_id: int
    doctor_id: int
    treatment_name: str
    diagnosis: str | None = None
    start_date: date
    end_date: date | None = None
    outcome: str | None = None
    notes: str | None = None


class TreatmentHistoryCreate(TreatmentHistoryBase):
    pass


class TreatmentHistoryUpdate(ORMBaseModel):
    treatment_name: str | None = None
    diagnosis: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    outcome: str | None = None
    notes: str | None = None


class TreatmentHistoryRead(TreatmentHistoryBase):
    treatment_id: int
    created_at: datetime


class VaccinationBase(ORMBaseModel):
    patient_id: int
    vaccine_name: str
    dose_number: int
    vaccination_date: date
    next_due_date: date | None = None
    remarks: str | None = None


class VaccinationCreate(VaccinationBase):
    pass


class VaccinationUpdate(ORMBaseModel):
    vaccine_name: str | None = None
    dose_number: int | None = None
    vaccination_date: date | None = None
    next_due_date: date | None = None
    remarks: str | None = None


class VaccinationRead(VaccinationBase):
    vaccination_id: int
    created_at: datetime


class AllergyBase(ORMBaseModel):
    patient_id: int
    allergy_name: str
    severity: SeverityLevel
    reaction: str | None = None
    notes: str | None = None


class AllergyCreate(AllergyBase):
    pass


class AllergyUpdate(ORMBaseModel):
    allergy_name: str | None = None
    severity: SeverityLevel | None = None
    reaction: str | None = None
    notes: str | None = None


class AllergyRead(AllergyBase):
    allergy_id: int
    created_at: datetime


class TimelineEvent(ORMBaseModel):
    event_date: date
    event_type: str
    title: str
    description: str | None = None
    source_id: int | None = None
