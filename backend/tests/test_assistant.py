from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.db.base  # noqa: F401
from app.ai_reports.service import AIReportService
from app.chatbot.service import ChatbotService
from app.models.assistant import ChatMessage, ChatSession
from app.models.base import Base
from app.models.user import User, UserRole
from app.rag.service import RAGService
from app.schemas.assistant import GeneratedReportCreate, KnowledgeDocumentCreate


def make_session(tmp_path: Path):
    engine = create_engine(f"sqlite:///{tmp_path / 'assistant_test.db'}", future=True)
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)()


def seed_user(db, role: UserRole = UserRole.admin) -> User:
    user = User(full_name="Admin User", email=f"{role.value.lower().replace(' ', '_')}@example.com", password_hash="hash", role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_rag_ingest_and_search(tmp_path) -> None:
    db = make_session(tmp_path)
    user = seed_user(db)
    rag = RAGService()
    rag.ingest_document(
        db,
        user,
        KnowledgeDocumentCreate(
            title="ICU Oxygen Policy",
            source_type="Hospital Policy",
            source_ref="POL-ICU-001",
            content="Oxygen cylinders must be checked twice daily. ICU escalation is required when oxygen saturation falls below threshold.",
            summary="ICU oxygen handling policy.",
            tags={"department": "ICU"},
        ),
    )
    results = rag.search(db, "When should ICU escalation happen?", top_k=3)
    assert results
    assert "ICU" in results[0].document_title


def test_chatbot_creates_session_and_message(tmp_path) -> None:
    db = make_session(tmp_path)
    user = seed_user(db)
    rag = RAGService()
    rag.ingest_document(
        db,
        user,
        KnowledgeDocumentCreate(
            title="Medication Reminder Policy",
            source_type="Hospital Policy",
            content="Patients should be reminded to take medication with food when prescribed.",
            summary="Medication reminder guidance.",
            tags={"audience": "patient"},
        ),
    )
    chatbot = ChatbotService(rag_service=rag)
    response = chatbot.send_message(
        db,
        user,
        {
            "chat_session_id": None,
            "audience": "admin",
            "language": "English",
            "patient_id": None,
            "message": "Show me the hospital knowledge about medication reminders.",
        },
    )
    assert response.chat_session.title
    assert response.confidence_score > 0
    assert response.assistant_message.content
    assert db.query(ChatSession).count() == 1
    assert db.query(ChatMessage).count() == 2


def test_report_generation_creates_files_and_records(tmp_path) -> None:
    db = make_session(tmp_path)
    user = seed_user(db)
    report_service = AIReportService(output_dir=tmp_path / "reports")
    report = report_service.generate_report(
        db,
        user.id,
        GeneratedReportCreate(
            report_type="Executive Summary",
            format="PDF",
            title="Monthly Executive Summary",
            summary="Hospital operations remained stable.",
            metadata_json={"narrative": "ICU occupancy remained stable through the month."},
        ),
    )
    assert Path(report.output_path).exists()
    assert report.file_name.endswith(".pdf")

