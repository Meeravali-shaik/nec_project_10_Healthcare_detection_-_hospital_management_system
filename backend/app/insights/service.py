from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.operations import AlertSeverity
from app.models.ai import DiseasePrediction, OutcomePrediction, RiskAssessment
from app.models.assistant import InsightReport
from app.models.operations import Bed, BedStatus, EmergencyAlert, Resource, Staff, StaffStatus
from app.schemas.assistant import ExecutiveInsightSummary, InsightReportCreate


class InsightService:
    def executive_summary(self, db: Session) -> ExecutiveInsightSummary:
        total_beds = db.scalar(select(func.count()).select_from(Bed)) or 0
        occupied_beds = db.scalar(select(func.count()).select_from(Bed).where(Bed.status == BedStatus.occupied)) or 0
        occupancy_rate = round((occupied_beds / total_beds) * 100, 2) if total_beds else 0.0
        critical_alerts = db.scalar(select(func.count()).select_from(EmergencyAlert).where(EmergencyAlert.severity == AlertSeverity.critical)) or 0
        staff_active = db.scalar(select(func.count()).select_from(Staff).where(Staff.status == StaffStatus.active)) or 0
        avg_risk = float(db.scalar(select(func.avg(DiseasePrediction.risk_score))) or 0.0)
        high_risk = db.scalar(select(func.count()).select_from(RiskAssessment).where(RiskAssessment.risk_category.in_(["High", "Critical"]))) or 0
        top_resource = db.execute(
            select(Resource.resource_name, func.sum(Resource.quantity_in_use))
            .group_by(Resource.resource_name)
            .order_by(func.sum(Resource.quantity_in_use).desc())
            .limit(1)
        ).first()

        occupancy_trend = f"Current occupancy is {occupancy_rate}% with {occupied_beds} occupied beds out of {total_beds}."
        resource_utilization = f"Top utilized resource: {top_resource[0] if top_resource else 'N/A'}."
        disease_trend = f"Average prediction risk is {round(avg_risk, 2)} with {high_risk} high-risk assessments."
        revenue_trend = "Revenue trend analysis is available once billing data is connected."
        staff_performance = f"{staff_active} staff members are active and monitoring ongoing care delivery."
        narrative = (
            f"Occupancy is at {occupancy_rate}% with {critical_alerts} critical alerts and {high_risk} high-risk patients requiring attention."
        )

        confidence = 0.72 if total_beds else 0.4
        return ExecutiveInsightSummary(
            occupancy_trend=occupancy_trend,
            resource_utilization=resource_utilization,
            disease_trend=disease_trend,
            revenue_trend=revenue_trend,
            staff_performance=staff_performance,
            confidence_score=confidence,
            narrative=narrative,
        )

    def create_report(self, db: Session, current_user_id: int | None, payload: InsightReportCreate) -> InsightReport:
        report = InsightReport(
            report_type=payload.report_type,
            title=payload.title,
            summary=payload.summary,
            narrative=payload.narrative,
            metrics_json=payload.metrics_json,
            audience=payload.audience,
            created_by=current_user_id,
            patient_id=payload.patient_id,
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        return report
