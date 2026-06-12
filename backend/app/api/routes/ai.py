from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db, require_roles
from app.models.ai import DiseasePrediction, MedicalAnalysisResult, OutcomePrediction, PredictionHistory, RiskAssessment, TreatmentRecommendation
from app.models.user import User, UserRole
from app.schemas.ai import (
    AIAnalyticsSummary,
    DiseasePredictionInput,
    DiseasePredictionRead,
    MedicalAnalysisResultRead,
    OutcomePredictionInput,
    OutcomePredictionRead,
    ReportAnalysisInput,
    RiskAssessmentRead,
    TreatmentRecommendationInput,
    TreatmentRecommendationRead,
)
from app.services.ai_service import AIService

router = APIRouter()
ai_service = AIService()


def _ensure_patient_scope(current_user: User, patient_id: int) -> None:
    if current_user.role == UserRole.patient:
        if not current_user.patient_profile or current_user.patient_profile.patient_id != patient_id:
            raise HTTPException(status_code=403, detail="Access denied")


@router.post("/disease-predictions", response_model=DiseasePredictionRead, dependencies=[Depends(require_roles(UserRole.admin, UserRole.staff, UserRole.doctor, UserRole.patient))])
def predict_disease(payload: DiseasePredictionInput, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _ensure_patient_scope(current_user, payload.patient_id)
    return ai_service.predict_disease(db, current_user, payload.model_dump())


@router.get("/disease-predictions")
def list_disease_predictions(
    patient_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = db.query(DiseasePrediction).order_by(DiseasePrediction.created_at.desc())
    if patient_id is not None:
        _ensure_patient_scope(current_user, patient_id)
        stmt = stmt.filter(DiseasePrediction.patient_id == patient_id)
    elif current_user.role == UserRole.patient:
        if not current_user.patient_profile:
            raise HTTPException(status_code=403, detail="Patient profile not found")
        stmt = stmt.filter(DiseasePrediction.patient_id == current_user.patient_profile.patient_id)
    return [DiseasePredictionRead.model_validate(item).model_dump() for item in stmt.all()]


@router.get("/prediction-history")
def list_prediction_history(
    patient_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = db.query(PredictionHistory).order_by(PredictionHistory.created_at.desc())
    if patient_id is not None:
        _ensure_patient_scope(current_user, patient_id)
        stmt = stmt.filter(PredictionHistory.patient_id == patient_id)
    elif current_user.role == UserRole.patient:
        if not current_user.patient_profile:
            raise HTTPException(status_code=403, detail="Patient profile not found")
        stmt = stmt.filter(PredictionHistory.patient_id == current_user.patient_profile.patient_id)
    return [
        {
            "history_id": item.history_id,
            "prediction_id": item.prediction_id,
            "patient_id": item.patient_id,
            "model_used": item.model_used,
            "disease": item.disease,
            "risk_score": item.risk_score,
            "confidence_score": item.confidence_score,
            "created_at": item.created_at,
        }
        for item in stmt.all()
    ]


@router.post("/treatment-recommendations", response_model=TreatmentRecommendationRead, dependencies=[Depends(require_roles(UserRole.admin, UserRole.staff, UserRole.doctor, UserRole.patient))])
def recommend_treatment(payload: TreatmentRecommendationInput, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _ensure_patient_scope(current_user, payload.patient_id)
    return ai_service.recommend_treatment(db, current_user, payload.model_dump())


@router.get("/treatment-recommendations")
def list_treatment_recommendations(
    patient_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = db.query(TreatmentRecommendation).order_by(TreatmentRecommendation.created_at.desc())
    if patient_id is not None:
        _ensure_patient_scope(current_user, patient_id)
        stmt = stmt.filter(TreatmentRecommendation.patient_id == patient_id)
    elif current_user.role == UserRole.patient:
        if not current_user.patient_profile:
            raise HTTPException(status_code=403, detail="Patient profile not found")
        stmt = stmt.filter(TreatmentRecommendation.patient_id == current_user.patient_profile.patient_id)
    return [TreatmentRecommendationRead.model_validate(item).model_dump() for item in stmt.all()]


@router.post("/outcome-predictions", response_model=OutcomePredictionRead, dependencies=[Depends(require_roles(UserRole.admin, UserRole.staff, UserRole.doctor, UserRole.patient))])
def predict_outcome(payload: OutcomePredictionInput, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _ensure_patient_scope(current_user, payload.patient_id)
    return ai_service.predict_outcome(db, current_user, payload.model_dump())


@router.get("/outcome-predictions")
def list_outcome_predictions(
    patient_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = db.query(OutcomePrediction).order_by(OutcomePrediction.created_at.desc())
    if patient_id is not None:
        _ensure_patient_scope(current_user, patient_id)
        stmt = stmt.filter(OutcomePrediction.patient_id == patient_id)
    elif current_user.role == UserRole.patient:
        if not current_user.patient_profile:
            raise HTTPException(status_code=403, detail="Patient profile not found")
        stmt = stmt.filter(OutcomePrediction.patient_id == current_user.patient_profile.patient_id)
    return [OutcomePredictionRead.model_validate(item).model_dump() for item in stmt.all()]


@router.post("/report-analysis", response_model=MedicalAnalysisResultRead, dependencies=[Depends(require_roles(UserRole.admin, UserRole.staff, UserRole.doctor, UserRole.patient))])
def analyze_report(payload: ReportAnalysisInput, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _ensure_patient_scope(current_user, payload.patient_id)
    return ai_service.analyze_report(db, current_user, payload.model_dump())


@router.get("/report-analysis")
def list_report_analysis(
    patient_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = db.query(MedicalAnalysisResult).order_by(MedicalAnalysisResult.created_at.desc())
    if patient_id is not None:
        _ensure_patient_scope(current_user, patient_id)
        stmt = stmt.filter(MedicalAnalysisResult.patient_id == patient_id)
    elif current_user.role == UserRole.patient:
        if not current_user.patient_profile:
            raise HTTPException(status_code=403, detail="Patient profile not found")
        stmt = stmt.filter(MedicalAnalysisResult.patient_id == current_user.patient_profile.patient_id)
    return [MedicalAnalysisResultRead.model_validate(item).model_dump() for item in stmt.all()]


@router.get("/risk-assessments", response_model=list[RiskAssessmentRead])
def list_risk_assessments(
    patient_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = db.query(RiskAssessment).order_by(RiskAssessment.created_at.desc())
    if patient_id is not None:
        _ensure_patient_scope(current_user, patient_id)
        stmt = stmt.filter(RiskAssessment.patient_id == patient_id)
    elif current_user.role == UserRole.patient:
        if not current_user.patient_profile:
            raise HTTPException(status_code=403, detail="Patient profile not found")
        stmt = stmt.filter(RiskAssessment.patient_id == current_user.patient_profile.patient_id)
    return stmt.all()


@router.post("/risk-assessments/{patient_id}", response_model=RiskAssessmentRead, dependencies=[Depends(require_roles(UserRole.admin, UserRole.staff, UserRole.doctor, UserRole.patient))])
def create_risk_assessment(patient_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _ensure_patient_scope(current_user, patient_id)
    return ai_service.risk_assessment(db, current_user, patient_id)


@router.get("/dashboard/summary", response_model=AIAnalyticsSummary, dependencies=[Depends(require_roles(UserRole.admin, UserRole.doctor, UserRole.staff, UserRole.patient))])
def analytics_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == UserRole.patient and not current_user.patient_profile:
        raise HTTPException(status_code=403, detail="Patient profile not found")
    return ai_service.analytics_summary(db)
