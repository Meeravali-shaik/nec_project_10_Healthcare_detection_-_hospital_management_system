from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.models.ai import AuditLog, DiseasePrediction, MedicalAnalysisResult, OutcomePrediction, PredictionHistory, RiskAssessment, TreatmentRecommendation
from app.models.user import User, UserRole
from app.schemas.ai import AIAnalyticsSummary
from app.ml.inference.service import DiseasePredictionService, OutcomePredictionService, RecommendationEngine, ReportAnalysisService


class AIService:
    def __init__(self) -> None:
        self.disease_service = DiseasePredictionService()
        self.outcome_service = OutcomePredictionService()
        self.recommendation_engine = RecommendationEngine()
        self.report_service = ReportAnalysisService()

    def _can_access_patient(self, current_user: User, patient_id: int) -> None:
        if current_user.role in {UserRole.admin, UserRole.staff}:
            return
        if current_user.role == UserRole.doctor:
            return
        if current_user.role == UserRole.patient and current_user.patient_profile and current_user.patient_profile.patient_id == patient_id:
            return
        raise AppError("Access denied.", 403)

    def _log_action(self, db: Session, current_user: User, action: str, entity_type: str, entity_id: int | str | None, patient_id: int | None, details: dict) -> None:
        db.add(
            AuditLog(
                user_id=current_user.id,
                patient_id=patient_id,
                action=action,
                entity_type=entity_type,
                entity_id=str(entity_id) if entity_id is not None else None,
                details=details,
            )
        )

    def predict_disease(self, db: Session, current_user: User, payload: dict) -> DiseasePrediction:
        self._can_access_patient(current_user, payload["patient_id"])
        result = self.disease_service.predict(payload)
        prediction = DiseasePrediction(
            patient_id=payload["patient_id"],
            model_used=result["model_used"],
            disease=result["disease"],
            risk_score=result["risk_score"],
            confidence_score=result["confidence_score"],
            severity_level=result["severity_level"],
            input_features=result["input_features"],
        )
        db.add(prediction)
        db.flush()
        history = PredictionHistory(
            prediction_id=prediction.prediction_id,
            patient_id=prediction.patient_id,
            model_used=prediction.model_used,
            disease=prediction.disease,
            risk_score=prediction.risk_score,
            confidence_score=prediction.confidence_score,
        )
        db.add(history)
        self._log_action(db, current_user, "create_prediction", "DiseasePrediction", prediction.prediction_id, prediction.patient_id, result)
        db.commit()
        db.refresh(prediction)
        return prediction

    def recommend_treatment(self, db: Session, current_user: User, payload: dict) -> TreatmentRecommendation:
        self._can_access_patient(current_user, payload["patient_id"])
        recommendation_payload = self.recommendation_engine.recommend(payload["disease"], payload.get("symptoms", []))
        recommendation = TreatmentRecommendation(patient_id=payload["patient_id"], disease=payload["disease"], **recommendation_payload)
        db.add(recommendation)
        self._log_action(db, current_user, "create_recommendation", "TreatmentRecommendation", None, recommendation.patient_id, recommendation_payload)
        db.commit()
        db.refresh(recommendation)
        return recommendation

    def predict_outcome(self, db: Session, current_user: User, payload: dict) -> OutcomePrediction:
        self._can_access_patient(current_user, payload["patient_id"])
        result = self.outcome_service.predict(payload)
        outcome = OutcomePrediction(
            patient_id=payload["patient_id"],
            disease=payload["disease"],
            severity=payload["severity"],
            input_features=payload,
            **result,
        )
        db.add(outcome)
        self._log_action(db, current_user, "create_outcome_prediction", "OutcomePrediction", None, outcome.patient_id, result)
        db.commit()
        db.refresh(outcome)
        return outcome

    def analyze_report(self, db: Session, current_user: User, payload: dict) -> MedicalAnalysisResult:
        self._can_access_patient(current_user, payload["patient_id"])
        result = self.report_service.analyze(payload["report_text"])
        analysis = MedicalAnalysisResult(
            patient_id=payload["patient_id"],
            report_id=payload.get("report_id"),
            **result,
        )
        db.add(analysis)
        db.flush()
        self._log_action(db, current_user, "analyze_report", "MedicalAnalysisResult", analysis.analysis_id, analysis.patient_id, result)
        db.commit()
        db.refresh(analysis)
        return analysis

    def risk_assessment(self, db: Session, current_user: User, patient_id: int) -> RiskAssessment:
        self._can_access_patient(current_user, patient_id)
        statement = select(DiseasePrediction).where(DiseasePrediction.patient_id == patient_id).order_by(DiseasePrediction.created_at.desc())
        predictions = list(db.scalars(statement).all())
        if not predictions:
            risk_score = 0.0
            category = "Low"
            factors = {}
        else:
            risk_score = round(sum(pred.risk_score for pred in predictions[:5]) / min(len(predictions), 5), 2)
            if risk_score < 25:
                category = "Low"
            elif risk_score < 50:
                category = "Medium"
            elif risk_score < 75:
                category = "High"
            else:
                category = "Critical"
            factors = {"recent_diseases": [pred.disease for pred in predictions[:5]]}
        assessment = RiskAssessment(patient_id=patient_id, risk_score=risk_score, risk_category=category, factors=factors)
        db.add(assessment)
        self._log_action(db, current_user, "create_risk_assessment", "RiskAssessment", None, patient_id, {"risk_score": risk_score, "risk_category": category, "factors": factors})
        db.commit()
        db.refresh(assessment)
        return assessment

    def analytics_summary(self, db: Session) -> AIAnalyticsSummary:
        total_predictions = db.scalar(select(func.count()).select_from(DiseasePrediction)) or 0
        high_risk_patients = db.scalar(select(func.count()).select_from(RiskAssessment).where(RiskAssessment.risk_category.in_(["High", "Critical"]))) or 0
        avg_risk_score = float(db.scalar(select(func.avg(DiseasePrediction.risk_score))) or 0.0)
        disease_counts = db.execute(select(DiseasePrediction.disease, func.count()).group_by(DiseasePrediction.disease)).all()
        disease_distribution = {row[0]: row[1] for row in disease_counts}
        top_disease = max(disease_distribution.items(), key=lambda item: item[1])[0] if disease_distribution else None
        return AIAnalyticsSummary(
            total_predictions=total_predictions,
            top_disease=top_disease,
            high_risk_patients=high_risk_patients,
            avg_risk_score=round(avg_risk_score, 2),
            disease_distribution=disease_distribution,
        )
