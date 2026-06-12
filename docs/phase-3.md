# Phase 3 Architecture

## Backend AI Package

- `app/models/ai.py`
- `app/schemas/ai.py`
- `app/services/ai_service.py`
- `app/api/routes/ai.py`
- `app/ml/preprocessing/`
- `app/ml/training/`
- `app/ml/inference/`
- `app/ml/evaluation/`
- `app/ml/recommendation/`

## ML Pipeline

1. Load or synthesize training data
2. Clean and encode features
3. Train Logistic Regression, Decision Tree, Random Forest, and optional XGBoost
4. Compare metrics
5. Persist the trained artifact with `joblib`
6. Load best model at inference time
7. Store prediction history and audit logs

## New Database Tables

- `DiseasePrediction`
- `PredictionHistory`
- `TreatmentRecommendation`
- `OutcomePrediction`
- `RiskAssessment`
- `MedicalAnalysisResult`
- `AuditLog`

## Frontend Pages

- `/ai`
- `/ai/disease-prediction`
- `/ai/outcome-prediction`
- `/ai/treatment-recommendation`
- `/ai/report-analysis`

## Deployment Notes

- Keep `ml_models/` outside version control in production and mount it as a persistent volume.
- Run the training job on a controlled schedule, then reload the app or restart workers to pick up new artifacts.
- Monitor drift using prediction logs and audit logs.

