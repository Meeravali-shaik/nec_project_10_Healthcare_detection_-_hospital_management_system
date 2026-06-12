from fastapi import APIRouter

from app.api.routes.appointments import router as appointments_router
from app.api.routes.auth import router as auth_router
from app.api.routes.ai import router as ai_router
from app.api.routes.assistant import router as assistant_router
from app.api.routes.ehr import router as ehr_router
from app.api.routes.doctors import router as doctors_router
from app.api.routes.patients import router as patients_router
from app.api.routes.operations import router as operations_router
from app.api.routes.users import router as users_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(patients_router, prefix="/patients", tags=["Patients"])
api_router.include_router(doctors_router, prefix="/doctors", tags=["Doctors"])
api_router.include_router(appointments_router, prefix="/appointments", tags=["Appointments"])
api_router.include_router(ehr_router, prefix="/ehr", tags=["EHR"])
api_router.include_router(ai_router, prefix="/ai", tags=["AI"])
api_router.include_router(assistant_router, prefix="/assistant", tags=["Assistant"])
api_router.include_router(operations_router, prefix="/operations", tags=["Operations"])
