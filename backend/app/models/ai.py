from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class DiseasePrediction(Base):
    __tablename__ = "disease_predictions"

    prediction_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.patient_id"), nullable=False, index=True)
    model_used: Mapped[str] = mapped_column(String(100), nullable=False)
    disease: Mapped[str] = mapped_column(String(100), nullable=False)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    severity_level: Mapped[str] = mapped_column(String(50), nullable=False)
    input_features: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


class PredictionHistory(Base):
    __tablename__ = "prediction_history"

    history_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    prediction_id: Mapped[int] = mapped_column(ForeignKey("disease_predictions.prediction_id"), nullable=False, index=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.patient_id"), nullable=False, index=True)
    model_used: Mapped[str] = mapped_column(String(100), nullable=False)
    disease: Mapped[str] = mapped_column(String(100), nullable=False)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


class TreatmentRecommendation(Base):
    __tablename__ = "treatment_recommendations"

    recommendation_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.patient_id"), nullable=False, index=True)
    disease: Mapped[str] = mapped_column(String(100), nullable=False)
    recommended_specialist: Mapped[str] = mapped_column(String(150), nullable=False)
    suggested_tests: Mapped[str] = mapped_column(Text, nullable=False)
    lifestyle_recommendations: Mapped[str] = mapped_column(Text, nullable=False)
    preliminary_treatment_guidance: Mapped[str] = mapped_column(Text, nullable=False)
    follow_up_suggestions: Mapped[str] = mapped_column(Text, nullable=False)
    rule_version: Mapped[str] = mapped_column(String(50), nullable=False, default="v1")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


class OutcomePrediction(Base):
    __tablename__ = "outcome_predictions"

    outcome_prediction_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.patient_id"), nullable=False, index=True)
    disease: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[str] = mapped_column(String(50), nullable=False)
    recovery_probability: Mapped[float] = mapped_column(Float, nullable=False)
    readmission_risk: Mapped[float] = mapped_column(Float, nullable=False)
    icu_requirement_risk: Mapped[float] = mapped_column(Float, nullable=False)
    mortality_risk: Mapped[float] = mapped_column(Float, nullable=False)
    expected_length_of_stay: Mapped[float] = mapped_column(Float, nullable=False)
    risk_category: Mapped[str] = mapped_column(String(50), nullable=False)
    clinical_recommendations: Mapped[str] = mapped_column(Text, nullable=False)
    input_features: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    risk_assessment_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.patient_id"), nullable=False, index=True)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    risk_category: Mapped[str] = mapped_column(String(50), nullable=False)
    factors: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


class MedicalAnalysisResult(Base):
    __tablename__ = "medical_analysis_results"

    analysis_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.patient_id"), nullable=False, index=True)
    report_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    extracted_text: Mapped[str] = mapped_column(Text, nullable=False)
    identified_values: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    abnormal_values: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    alert_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    audit_log_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    patient_id: Mapped[int | None] = mapped_column(ForeignKey("patients.patient_id"), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    details: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
