from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path

from app.core.dependencies import get_current_user, get_db, require_roles
from app.models.ehr import Allergy, LabReport, MedicalRecord, Prescription, ReportType, SeverityLevel, TreatmentHistory, Vaccination
from app.models.user import User, UserRole
from app.schemas.ehr import (
    AllergyCreate,
    AllergyRead,
    AllergyUpdate,
    LabReportRead,
    MedicalRecordCreate,
    MedicalRecordRead,
    MedicalRecordUpdate,
    PrescriptionCreate,
    PrescriptionRead,
    PrescriptionUpdate,
    TreatmentHistoryCreate,
    TreatmentHistoryRead,
    TreatmentHistoryUpdate,
    VaccinationCreate,
    VaccinationRead,
    VaccinationUpdate,
)
from app.services.ehr_service import (
    build_patient_timeline,
    build_my_timeline,
    create_allergy,
    create_lab_report,
    create_medical_record,
    create_prescription,
    create_treatment,
    create_vaccination,
    get_lab_report,
    get_medical_record,
    get_prescription,
    list_allergies,
    list_lab_reports,
    list_medical_records,
    list_prescriptions,
    list_treatments,
    list_vaccinations,
    paginate_query,
    serialize_lab_report,
    serialize_prescription,
    update_allergy,
    update_medical_record,
    update_prescription,
    update_treatment,
    update_vaccination,
)

router = APIRouter()


def _meta_response(items, meta):
    return {"items": items, "meta": meta}


@router.get("/patients/{patient_id}/timeline")
def patient_timeline(patient_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return build_patient_timeline(db, patient_id, current_user)


@router.get("/me/timeline")
def my_timeline(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return build_my_timeline(db, current_user)


@router.get("/medical-records")
def medical_records(
    search: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, meta = list_medical_records(db, current_user, search, page, size)
    return _meta_response([MedicalRecordRead.model_validate(item).model_dump() for item in items], meta.model_dump())


@router.post("/medical-records", response_model=MedicalRecordRead, dependencies=[Depends(require_roles(UserRole.admin, UserRole.staff, UserRole.doctor))])
def create_record(payload: MedicalRecordCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_medical_record(db, payload, current_user)


@router.get("/medical-records/{record_id}", response_model=MedicalRecordRead)
def read_record(record_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    record = get_medical_record(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Medical record not found")
    if current_user.role == UserRole.patient and (not current_user.patient_profile or current_user.patient_profile.patient_id != record.patient_id):
        raise HTTPException(status_code=403, detail="Access denied")
    return record


@router.put("/medical-records/{record_id}", response_model=MedicalRecordRead, dependencies=[Depends(require_roles(UserRole.admin, UserRole.staff, UserRole.doctor))])
def edit_record(record_id: int, payload: MedicalRecordUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    record = get_medical_record(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Medical record not found")
    return update_medical_record(db, record, payload, current_user)


@router.get("/prescriptions")
def prescriptions(
    search: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, meta = list_prescriptions(db, current_user, search, page, size)
    return _meta_response([serialize_prescription(item) for item in items], meta.model_dump())


@router.post("/prescriptions", response_model=PrescriptionRead, dependencies=[Depends(require_roles(UserRole.admin, UserRole.staff, UserRole.doctor))])
def create_rx(payload: PrescriptionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_prescription(db, payload, current_user)


@router.get("/prescriptions/{prescription_id}", response_model=PrescriptionRead)
def read_rx(prescription_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    prescription = get_prescription(db, prescription_id)
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    if current_user.role == UserRole.patient and (not current_user.patient_profile or current_user.patient_profile.patient_id != prescription.patient_id):
        raise HTTPException(status_code=403, detail="Access denied")
    return prescription


@router.put("/prescriptions/{prescription_id}", response_model=PrescriptionRead, dependencies=[Depends(require_roles(UserRole.admin, UserRole.staff, UserRole.doctor))])
def edit_rx(prescription_id: int, payload: PrescriptionUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    prescription = get_prescription(db, prescription_id)
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    return update_prescription(db, prescription, payload, current_user)


@router.get("/prescriptions/{prescription_id}/download")
def download_rx(prescription_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    prescription = get_prescription(db, prescription_id)
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    if current_user.role == UserRole.patient and (not current_user.patient_profile or current_user.patient_profile.patient_id != prescription.patient_id):
        raise HTTPException(status_code=403, detail="Access denied")

    export_path = _generate_prescription_export(prescription)
    return FileResponse(path=export_path, filename=Path(export_path).name)


@router.get("/lab-reports")
def lab_reports(
    search: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, meta = list_lab_reports(db, current_user, search, page, size)
    return _meta_response([serialize_lab_report(item) for item in items], meta.model_dump())


@router.post("/lab-reports", response_model=LabReportRead, dependencies=[Depends(require_roles(UserRole.admin, UserRole.staff))])
def upload_report(
    patient_id: int = Form(...),
    report_type: ReportType = Form(...),
    description: str | None = Form(default=None),
    upload: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_lab_report(db, patient_id, current_user, upload, report_type, description)


@router.get("/lab-reports/{report_id}", response_model=LabReportRead)
def read_report(report_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    report = get_lab_report(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Lab report not found")
    if current_user.role == UserRole.patient and (not current_user.patient_profile or current_user.patient_profile.patient_id != report.patient_id):
        raise HTTPException(status_code=403, detail="Access denied")
    return report


@router.get("/lab-reports/{report_id}/download")
def download_report(report_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    report = get_lab_report(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Lab report not found")
    if current_user.role == UserRole.patient and (not current_user.patient_profile or current_user.patient_profile.patient_id != report.patient_id):
        raise HTTPException(status_code=403, detail="Access denied")
    return FileResponse(report.file_path, filename=report.file_name)


@router.get("/treatments")
def treatments(
    search: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, meta = list_treatments(db, current_user, search, page, size)
    return _meta_response([TreatmentHistoryRead.model_validate(item).model_dump() for item in items], meta.model_dump())


@router.post("/treatments", response_model=TreatmentHistoryRead, dependencies=[Depends(require_roles(UserRole.admin, UserRole.staff, UserRole.doctor))])
def create_treatment_record(payload: TreatmentHistoryCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_treatment(db, payload, current_user)


@router.put("/treatments/{treatment_id}", response_model=TreatmentHistoryRead, dependencies=[Depends(require_roles(UserRole.admin, UserRole.staff, UserRole.doctor))])
def edit_treatment_record(treatment_id: int, payload: TreatmentHistoryUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    treatment = db.get(TreatmentHistory, treatment_id)
    if not treatment:
        raise HTTPException(status_code=404, detail="Treatment not found")
    return update_treatment(db, treatment, payload, current_user)


@router.get("/vaccinations")
def vaccinations(
    search: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, meta = list_vaccinations(db, current_user, search, page, size)
    return _meta_response([VaccinationRead.model_validate(item).model_dump() for item in items], meta.model_dump())


@router.post("/vaccinations", response_model=VaccinationRead, dependencies=[Depends(require_roles(UserRole.admin, UserRole.staff, UserRole.doctor))])
def create_vaccination_record(payload: VaccinationCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_vaccination(db, payload, current_user)


@router.put("/vaccinations/{vaccination_id}", response_model=VaccinationRead, dependencies=[Depends(require_roles(UserRole.admin, UserRole.staff, UserRole.doctor))])
def edit_vaccination_record(vaccination_id: int, payload: VaccinationUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    vaccination = db.get(Vaccination, vaccination_id)
    if not vaccination:
        raise HTTPException(status_code=404, detail="Vaccination not found")
    return update_vaccination(db, vaccination, payload, current_user)


@router.get("/allergies")
def allergies(
    search: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, meta = list_allergies(db, current_user, search, page, size)
    return _meta_response([AllergyRead.model_validate(item).model_dump() for item in items], meta.model_dump())


@router.post("/allergies", response_model=AllergyRead, dependencies=[Depends(require_roles(UserRole.admin, UserRole.staff, UserRole.doctor))])
def create_allergy_record(payload: AllergyCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_allergy(db, payload, current_user)


@router.put("/allergies/{allergy_id}", response_model=AllergyRead, dependencies=[Depends(require_roles(UserRole.admin, UserRole.staff, UserRole.doctor))])
def edit_allergy_record(allergy_id: int, payload: AllergyUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    allergy = db.get(Allergy, allergy_id)
    if not allergy:
        raise HTTPException(status_code=404, detail="Allergy not found")
    return update_allergy(db, allergy, payload, current_user)


def _write_temp_text(content: str, filename: str) -> str:
    from pathlib import Path

    output_dir = Path("storage") / "exports"
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / filename
    path.write_text(content, encoding="utf-8")
    return str(path)


def _generate_prescription_export(prescription: Prescription) -> str:
    from pathlib import Path

    output_dir = Path("storage") / "exports"
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = output_dir / f"prescription_{prescription.prescription_id}.pdf"

    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas

        c = canvas.Canvas(str(pdf_path), pagesize=A4)
        width, height = A4
        y = height - 50
        lines = [
            "Prescription",
            f"Prescription ID: {prescription.prescription_id}",
            f"Patient ID: {prescription.patient_id}",
            f"Doctor ID: {prescription.doctor_id}",
            f"Issue Date: {prescription.issue_date}",
            f"Instructions: {prescription.instructions or ''}",
            "Medications:",
        ] + [
            f"- {med.name} | {med.dosage or ''} | {med.frequency or ''} | {med.duration or ''}"
            for med in prescription.medications
        ]
        for line in lines:
            c.drawString(50, y, line[:100])
            y -= 18
            if y < 60:
                c.showPage()
                y = height - 50
        c.save()
        return str(pdf_path)
    except Exception:
        fallback = pdf_path.with_suffix(".txt")
        text = "\n".join(
            [
                "Prescription",
                f"Prescription ID: {prescription.prescription_id}",
                f"Patient ID: {prescription.patient_id}",
                f"Doctor ID: {prescription.doctor_id}",
                f"Issue Date: {prescription.issue_date}",
                f"Instructions: {prescription.instructions or ''}",
                "Medications:",
                *[
                    f"- {med.name} | {med.dosage or ''} | {med.frequency or ''} | {med.duration or ''}"
                    for med in prescription.medications
                ],
            ]
        )
        return _write_temp_text(text, fallback.name)
