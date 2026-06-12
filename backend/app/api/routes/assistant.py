from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai_reports.service import AIReportService
from app.chatbot.service import ChatbotService
from app.copilots.service import CopilotService
from app.core.dependencies import get_current_user, get_db, require_roles
from app.insights.service import InsightService
from app.memory.service import MemoryService
from app.models.assistant import AssistantMemory, ChatMessage, ChatSession, GeneratedReport, InsightReport, KnowledgeDocument, NotificationTemplate
from app.models.user import User, UserRole
from app.rag.service import RAGService
from app.schemas.assistant import (
    AssistantMemoryRead,
    ChatMessageRead,
    ChatRequest,
    ChatResponse,
    ChatSessionCreate,
    ChatSessionRead,
    CopilotSummary,
    GeneratedReportCreate,
    GeneratedReportRead,
    InsightReportCreate,
    InsightReportRead,
    ExecutiveInsightSummary,
    KnowledgeDocumentCreate,
    KnowledgeDocumentRead,
    KnowledgeSearchRequest,
    KnowledgeSearchResult,
    NotificationTemplateCreate,
    NotificationTemplateRead,
)

router = APIRouter()
chatbot_service = ChatbotService()
rag_service = RAGService()
copilot_service = CopilotService()
memory_service = MemoryService()
insight_service = InsightService()
report_service = AIReportService()


def _patient_scope(current_user: User, patient_id: int | None) -> None:
    if current_user.role == UserRole.patient and current_user.patient_profile and patient_id is not None:
        if current_user.patient_profile.patient_id != patient_id:
            raise HTTPException(status_code=403, detail="Access denied")
    elif current_user.role == UserRole.patient and not current_user.patient_profile:
        raise HTTPException(status_code=403, detail="Patient profile not found")


@router.post("/sessions", response_model=ChatSessionRead)
def create_session(payload: ChatSessionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _patient_scope(current_user, payload.patient_id)
    return chatbot_service.create_session(db, current_user, payload)


@router.get("/sessions", response_model=list[ChatSessionRead])
def list_sessions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return chatbot_service.list_sessions(db, current_user)


@router.get("/sessions/{session_id}/messages", response_model=list[ChatMessageRead])
def list_messages(session_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return chatbot_service.list_messages(db, current_user, session_id)


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _patient_scope(current_user, payload.patient_id)
    return chatbot_service.send_message(db, current_user, payload)


@router.post("/knowledge", response_model=KnowledgeDocumentRead, dependencies=[Depends(require_roles(UserRole.admin, UserRole.staff, UserRole.doctor))])
def ingest_knowledge(payload: KnowledgeDocumentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    document = rag_service.ingest_document(db, current_user, payload)
    return KnowledgeDocumentRead.model_validate(document)


@router.get("/knowledge", response_model=list[KnowledgeDocumentRead])
def list_knowledge(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    stmt = select(KnowledgeDocument).order_by(KnowledgeDocument.created_at.desc())
    return list(db.scalars(stmt).all())


@router.post("/knowledge/search", response_model=list[KnowledgeSearchResult])
def search_knowledge(payload: KnowledgeSearchRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return rag_service.search(db, payload.query, top_k=payload.top_k)


@router.get("/copilots/patient/{patient_id}", response_model=CopilotSummary)
def patient_copilot(patient_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _patient_scope(current_user, patient_id)
    return copilot_service.patient_assistant(db, patient_id)


@router.get("/copilots/doctor/{patient_id}", response_model=CopilotSummary, dependencies=[Depends(require_roles(UserRole.admin, UserRole.staff, UserRole.doctor))])
def doctor_copilot(patient_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _patient_scope(current_user, patient_id)
    return copilot_service.doctor_copilot(db, patient_id)


@router.get("/copilots/admin", response_model=CopilotSummary, dependencies=[Depends(require_roles(UserRole.admin, UserRole.staff))])
def admin_copilot(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return copilot_service.admin_overview(db)


@router.get("/insights/executive", response_model=ExecutiveInsightSummary, dependencies=[Depends(require_roles(UserRole.admin, UserRole.staff, UserRole.doctor))])
def executive_insights(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return insight_service.executive_summary(db)


@router.post("/insights/reports", response_model=InsightReportRead, dependencies=[Depends(require_roles(UserRole.admin, UserRole.staff, UserRole.doctor))])
def create_insight_report(payload: InsightReportCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    report = insight_service.create_report(db, current_user.id, payload)
    return InsightReportRead.model_validate(report)


@router.get("/insights/reports", response_model=list[InsightReportRead], dependencies=[Depends(require_roles(UserRole.admin, UserRole.staff, UserRole.doctor))])
def list_insight_reports(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    stmt = select(InsightReport).order_by(InsightReport.created_at.desc())
    return list(db.scalars(stmt).all())


@router.post("/reports", response_model=GeneratedReportRead, dependencies=[Depends(require_roles(UserRole.admin, UserRole.staff, UserRole.doctor))])
def generate_report(payload: GeneratedReportCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    report = report_service.generate_report(db, current_user.id, payload)
    return GeneratedReportRead.model_validate(report)


@router.get("/reports", response_model=list[GeneratedReportRead])
def list_reports(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    stmt = select(GeneratedReport).order_by(GeneratedReport.created_at.desc())
    return list(db.scalars(stmt).all())


@router.get("/memory/{session_id}", response_model=list[AssistantMemoryRead])
def list_memory(session_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    session = db.get(ChatSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    _patient_scope(current_user, session.patient_id)
    return memory_service.get_session_memory(db, session_id)


@router.get("/templates", response_model=list[NotificationTemplateRead], dependencies=[Depends(require_roles(UserRole.admin, UserRole.staff))])
def list_templates(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    stmt = select(NotificationTemplate).order_by(NotificationTemplate.created_at.desc())
    return list(db.scalars(stmt).all())


@router.post("/templates", response_model=NotificationTemplateRead, dependencies=[Depends(require_roles(UserRole.admin, UserRole.staff))])
def create_template(payload: NotificationTemplateCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    template = NotificationTemplate(**payload.model_dump())
    db.add(template)
    db.commit()
    db.refresh(template)
    return template

