from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import api_router
from app.core.config import settings
from app.core.errors import register_exception_handlers
from app.db.init_db import init_db


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI-Powered Healthcare Prediction & Resource Management System",
        version="1.0.0",
        description="Backend for authentication, patient, doctor, appointment, EHR, AI, and hospital operations management.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
        "http://localhost:5173",
        "https://nec-project-10-healthcare-detection-2cx5.onrender.com"
    ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)
    app.include_router(api_router, prefix="/api/v1")

    @app.on_event("startup")
    def on_startup() -> None:
        init_db()

    @app.get("/health", tags=["Health"])
    def health_check() -> dict[str, str]:
        return {"status": "healthy"}

    return app


app = create_app()
