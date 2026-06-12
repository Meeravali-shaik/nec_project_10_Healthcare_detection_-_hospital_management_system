from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.models.operations import AlertSeverity, EmergencyAlert
from app.models.user import User, UserRole
from app.schemas.operations import EmergencyAlertCreate


class EmergencyService:
    def create_alert(self, db: Session, current_user: User, payload: EmergencyAlertCreate) -> EmergencyAlert:
        if current_user.role not in {UserRole.admin, UserRole.staff, UserRole.doctor}:
            raise AppError("Access denied.", 403)
        alert = EmergencyAlert(**payload.model_dump())
        db.add(alert)
        db.commit()
        db.refresh(alert)
        return alert

    def list_alerts(self, db: Session, severity: AlertSeverity | None = None) -> list[EmergencyAlert]:
        stmt = select(EmergencyAlert).order_by(EmergencyAlert.timestamp.desc())
        if severity is not None:
            stmt = stmt.where(EmergencyAlert.severity == severity)
        return list(db.scalars(stmt).all())

    def detect_alerts(self, payload: dict) -> list[dict]:
        alerts = []
        if float(payload.get("oxygen_level", 100)) < 85:
            alerts.append({"alert_type": "Oxygen Level Below Threshold", "severity": "Critical", "message": "Oxygen levels are dangerously low."})
        if float(payload.get("icu_occupancy", 0)) >= 95:
            alerts.append({"alert_type": "ICU Capacity Exceeded", "severity": "Critical", "message": "ICU occupancy is above threshold."})
        if float(payload.get("bed_availability", 100)) < 10:
            alerts.append({"alert_type": "Bed Availability Critical", "severity": "High", "message": "Bed availability has reached a critical level."})
        if payload.get("emergency_patient_arrival"):
            alerts.append({"alert_type": "Emergency Patient Arrival", "severity": "High", "message": "Emergency patient requires immediate triage."})
        if payload.get("equipment_failure"):
            alerts.append({"alert_type": "Equipment Failure", "severity": "High", "message": "Medical equipment failure detected."})
        return alerts

