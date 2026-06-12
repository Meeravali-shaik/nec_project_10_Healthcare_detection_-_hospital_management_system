from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ORMBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class DiseasePredictionInput(BaseModel):
    patient_id: int
    age: int
    gender: str
    bmi: float
    blood_pressure: float
    glucose_level: float
    cholesterol: float
    family_history: str | None = None
    symptoms: list[str] = Field(default_factory=list)
    medical_history: str | None = None


class DiseasePredictionRead(ORMBaseModel):
    prediction_id: int
    patient_id: int
    model_used: str
    disease: str
    risk_score: float
    confidence_score: float
    severity_level: str
    created_at: datetime


class TreatmentRecommendationInput(BaseModel):
    patient_id: int
    disease: str
    symptoms: list[str] = Field(default_factory=list)


class TreatmentRecommendationRead(ORMBaseModel):
    recommendation_id: int
    patient_id: int
    disease: str
    recommended_specialist: str
    suggested_tests: str
    lifestyle_recommendations: str
    preliminary_treatment_guidance: str
    follow_up_suggestions: str
    rule_version: str
    created_at: datetime


class OutcomePredictionInput(BaseModel):
    patient_id: int
    disease: str
    severity: str
    age: int
    existing_conditions: list[str] = Field(default_factory=list)
    treatment_history: str | None = None
    lab_values: dict[str, float] = Field(default_factory=dict)


class OutcomePredictionRead(ORMBaseModel):
    outcome_prediction_id: int
    patient_id: int
    disease: str
    severity: str
    recovery_probability: float
    readmission_risk: float
    icu_requirement_risk: float
    mortality_risk: float
    expected_length_of_stay: float
    risk_category: str
    clinical_recommendations: str
    created_at: datetime


class ReportAnalysisInput(BaseModel):
    patient_id: int
    report_id: int | None = None
    report_text: str


class MedicalAnalysisResultRead(ORMBaseModel):
    analysis_id: int
    patient_id: int
    report_id: int | None
    extracted_text: str
    identified_values: dict
    abnormal_values: dict
    alert_message: str | None
    summary: str
    created_at: datetime


class RiskAssessmentRead(ORMBaseModel):
    risk_assessment_id: int
    patient_id: int
    risk_score: float
    risk_category: str
    factors: dict
    created_at: datetime


class AIAnalyticsSummary(BaseModel):
    total_predictions: int
    top_disease: str | None = None
    high_risk_patients: int
    avg_risk_score: float
    disease_distribution: dict[str, int]
