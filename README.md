# AI-Powered Healthcare Prediction & Resource Management System
url: https://nec-project-10-healthcare-detection-blc9.onrender.com
output:<img width="1918" height="917" alt="image" src="https://github.com/user-attachments/assets/a620adb6-cfdb-4f5a-a00e-387350239367" />
<img width="1918" height="886" alt="image" src="https://github.com/user-attachments/assets/63eb5334-1abf-4966-a403-99f7625296aa" />


Phase 1 delivers the foundational hospital management stack:

- Authentication and user management
- Patient management
- Doctor management
- Appointment scheduling

## Project Structure

- `backend/` FastAPI + SQLAlchemy + JWT + Pydantic
- `frontend/` React + Vite + Tailwind CSS
- `docs/` implementation notes and API overview

## Phase 2

The EHR layer adds:

- Medical records
- Prescriptions with medication line items
- Lab report uploads and downloads
- Treatment history
- Vaccinations
- Allergies
- Patient timeline views

## Phase 3

The AI Intelligence Engine adds:

- Disease prediction
- Outcome prediction
- Treatment recommendations
- Report analysis
- Risk scoring
- AI analytics dashboard

## Phase 4

The operations intelligence layer adds:

- Bed and ward management
- Resource inventory tracking
- Forecasting and operational planning
- Staff management and scheduling recommendations
- Emergency alerts and notifications
- Resource optimization recommendations

## Backend Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

If you already created the backend virtual environment, reinstall dependencies after pulling the latest requirements so `bcrypt==4.0.1` is used consistently.
If you want prescription PDF export support, keep `reportlab` installed from `backend/requirements.txt`.
For the AI layer, install the backend ML packages from `backend/requirements.txt`, then run `python -m app.ml.training.train_models` from the backend directory when you want to generate model artifacts.
For the operations forecasting layer, run `python -m app.forecasting.training.train_forecasts` once you wire in real historical data or keep the heuristic forecasts for development.

## Frontend Setup

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

## API Base

- Backend: `http://localhost:8000`
- API: `http://localhost:8000/api/v1`
- Frontend: `http://localhost:5173`

## Testing

- Backend health check: `GET /health`
- Backend docs: `http://localhost:8000/docs`
- Frontend login/register/dashboard routes after creating a user
