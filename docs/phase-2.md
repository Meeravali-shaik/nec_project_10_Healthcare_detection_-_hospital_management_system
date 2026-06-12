# Phase 2 Architecture

## Backend Modules

- `app/models/ehr.py`
- `app/schemas/ehr.py`
- `app/services/ehr_service.py`
- `app/api/routes/ehr.py`

## New Entities

- MedicalRecord
- Prescription
- Medication
- LabReport
- TreatmentHistory
- Vaccination
- Allergy

## Key APIs

- `GET /api/v1/ehr/medical-records`
- `POST /api/v1/ehr/medical-records`
- `GET /api/v1/ehr/prescriptions`
- `POST /api/v1/ehr/prescriptions`
- `GET /api/v1/ehr/lab-reports`
- `POST /api/v1/ehr/lab-reports`
- `GET /api/v1/ehr/treatments`
- `POST /api/v1/ehr/treatments`
- `GET /api/v1/ehr/vaccinations`
- `POST /api/v1/ehr/vaccinations`
- `GET /api/v1/ehr/allergies`
- `POST /api/v1/ehr/allergies`
- `GET /api/v1/ehr/me/timeline`

## Frontend Pages

- `/ehr`
- `/ehr/medical-records`
- `/ehr/prescriptions`
- `/ehr/lab-reports`
- `/ehr/treatments`
- `/ehr/vaccinations`
- `/ehr/allergies`
- `/ehr/timeline`

