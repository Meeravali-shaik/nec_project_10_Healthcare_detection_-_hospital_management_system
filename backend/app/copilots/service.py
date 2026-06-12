from __future__ import annotations

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.ai import DiseasePrediction, OutcomePrediction, RiskAssessment
from app.models.appointment import Appointment
from app.models.ehr import LabReport, MedicalRecord, Prescription, Vaccination, Allergy
from app.models.patient import Patient
from app.models.user import User
from app.schemas.assistant import CitationRead, CopilotSummary


class CopilotService:
    def _patient_citations(self, patient: Patient) -> list[CitationRead]:
        citations: list[CitationRead] = []
        if patient.family_history:
            citations.append(
                CitationRead(
                    document_title=f"Patient {patient.full_name} Profile",
                    source_type="Patient Profile",
                    source_ref=str(patient.patient_id),
                    chunk_index=0,
                    score=1.0,
                    excerpt=patient.family_history[:300],
                )
            )
        return citations

    def patient_assistant(self, db: Session, patient_id: int) -> CopilotSummary:
        patient = db.get(Patient, patient_id)
        if not patient:
            return CopilotSummary(audience="Patient", title="Patient Assistant", summary="Patient profile not found.", confidence_score=0.0)

        recent_prescriptions = list(db.scalars(select(Prescription).where(Prescription.patient_id == patient_id).order_by(Prescription.issue_date.desc()).limit(3)).all())
        recent_records = list(db.scalars(select(MedicalRecord).where(MedicalRecord.patient_id == patient_id).order_by(MedicalRecord.visit_date.desc()).limit(3)).all())
        vaccinations = list(db.scalars(select(Vaccination).where(Vaccination.patient_id == patient_id).order_by(Vaccination.vaccination_date.desc()).limit(3)).all())
        allergies = list(db.scalars(select(Allergy).where(Allergy.patient_id == patient_id)).all())

        summary = f"{patient.full_name} is a {patient.age or 'unknown age'} year old patient with {len(allergies)} recorded allergy entries."
        recommendations = []
        if allergies:
            recommendations.append("Review allergy history before new prescriptions.")
        if recent_prescriptions:
            recommendations.append("Track medication adherence and refill windows.")
        if vaccinations:
            next_due = next((item.next_due_date for item in vaccinations if item.next_due_date), None)
            if next_due:
                recommendations.append(f"Upcoming vaccination follow-up on {next_due.isoformat()}.")
        if not recommendations:
            recommendations.append("Keep up routine follow-up and preventive care.")

        return CopilotSummary(
            audience="Patient",
            title=f"Health Assistant for {patient.full_name}",
            summary=summary,
            recommendations=recommendations,
            citations=self._patient_citations(patient),
            confidence_score=0.82,
        )

    def doctor_copilot(self, db: Session, patient_id: int) -> CopilotSummary:
        patient = db.get(Patient, patient_id)
        if not patient:
            return CopilotSummary(audience="Doctor", title="Doctor Copilot", summary="Patient profile not found.", confidence_score=0.0)

        latest_prediction = db.scalar(select(RiskAssessment).where(RiskAssessment.patient_id == patient_id).order_by(RiskAssessment.created_at.desc()))
        latest_disease = db.scalar(select(DiseasePrediction).where(DiseasePrediction.patient_id == patient_id).order_by(DiseasePrediction.created_at.desc()))
        latest_outcome = db.scalar(select(OutcomePrediction).where(OutcomePrediction.patient_id == patient_id).order_by(OutcomePrediction.created_at.desc()))
        recent_appointments = list(db.scalars(select(Appointment).where(Appointment.patient_id == patient_id).order_by(Appointment.appointment_date.desc()).limit(3)).all())

        summary_bits = [
            f"Age: {patient.age or 'Unknown'}",
            f"Recent appointments: {len(recent_appointments)}",
        ]
        if latest_prediction:
            summary_bits.append(f"Risk category: {latest_prediction.risk_category} ({latest_prediction.risk_score})")
        if latest_disease:
            summary_bits.append(f"Latest disease prediction: {latest_disease.disease} ({latest_disease.severity_level})")
        if latest_outcome:
            summary_bits.append(f"Latest outcome risk: {latest_outcome.risk_category}")

        recommendations = [
            "Review recent labs and medication adherence.",
            "Escalate specialty review if risk is high or critical.",
        ]
        if latest_outcome and latest_outcome.icu_requirement_risk >= 0.5:
            recommendations.append("Consider close monitoring for ICU escalation.")

        citations = [
            CitationRead(
                document_title=f"Patient {patient.full_name} Profile",
                source_type="Patient Profile",
                source_ref=str(patient.patient_id),
                chunk_index=0,
                score=1.0,
                excerpt=patient.medical_history[:300] if patient.medical_history else "",
            )
        ]

        return CopilotSummary(
            audience="Doctor",
            title=f"Clinical Copilot for {patient.full_name}",
            summary="; ".join(summary_bits),
            recommendations=recommendations,
            citations=citations,
            confidence_score=0.88,
        )

    def admin_overview(self, db: Session) -> CopilotSummary:
        total_patients = db.scalar(select(func.count()).select_from(Patient)) or 0
        return CopilotSummary(
            audience="Admin",
            title="Administrative Assistant",
            summary=f"Operational oversight across occupancy, staffing, and AI reporting for {total_patients} registered patients.",
            recommendations=[
                "Review occupancy dashboards for high-risk wards.",
                "Monitor resource utilization and forecasted demand.",
                "Follow up on critical alerts and pending notifications.",
            ],
            confidence_score=0.74,
        )
