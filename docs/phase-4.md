# Phase 4 Architecture

## Backend Modules

- `app/models/operations.py`
- `app/schemas/operations.py`
- `app/resource_management/service.py`
- `app/forecasting/service.py`
- `app/forecasting/training/pipeline.py`
- `app/scheduling/service.py`
- `app/emergency/service.py`
- `app/notifications/service.py`
- `app/optimization/service.py`
- `app/api/routes/operations.py`

## Database Models

- Bed
- Ward
- Resource
- ResourceUsage
- ResourceForecast
- Staff
- StaffSchedule
- EmergencyAlert
- Notification
- OptimizationRecommendation

## Forecasting Design

- ARIMA fallback pipeline
- Prophet-compatible branch
- XGBoost regression branch
- LSTM-compatible branch
- Heuristic fallback when heavy ML dependencies are unavailable

## API Surface

- `GET /api/v1/operations/dashboard/summary`
- `GET /api/v1/operations/wards`
- `GET /api/v1/operations/beds`
- `GET /api/v1/operations/resources`
- `GET /api/v1/operations/staff`
- `GET /api/v1/operations/alerts`
- `GET /api/v1/operations/notifications`
- `GET /api/v1/operations/forecast/resource-demand`
- `POST /api/v1/operations/optimization/recommendations`
- `POST /api/v1/operations/scheduling/recommendations`

## Frontend Pages

- `/operations`
- `/operations/beds`
- `/operations/wards`
- `/operations/resources`
- `/operations/forecast`
- `/operations/staff`
- `/operations/scheduling`
- `/operations/emergency`
- `/operations/notifications`

## Deployment Notes

- Mount forecast artifacts as persistent storage in Docker.
- Move the SQLite database to PostgreSQL for production.
- Schedule forecasting jobs as background tasks or CI-driven jobs.
- Use audit logs and notification logs for compliance and traceability.

