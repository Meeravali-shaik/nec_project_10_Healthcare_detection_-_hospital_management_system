from __future__ import annotations

from datetime import datetime, timezone
from difflib import SequenceMatcher

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.copilots.service import CopilotService
from app.core.errors import AppError
from app.memory.service import MemoryService
from app.models.ai import AuditLog
from app.models.assistant import ChatMessage, ChatSession
from app.models.patient import Patient
from app.models.user import User, UserRole
from app.rag.service import RAGService
from app.schemas.assistant import CitationRead, ChatMessageCreate, ChatMessageRead, ChatRequest, ChatResponse, ChatSessionCreate, ChatSessionRead


LANGUAGE_WRAPPERS = {
    "Hindi": {
        "disclaimer": "AI-generated recommendations are intended to support healthcare professionals and should not replace clinical judgment.",
        "prefix": "सुरक्षित स्वास्थ्य सहायक:",
    },
    "Telugu": {
        "disclaimer": "AI-generated recommendations are intended to support healthcare professionals and should not replace clinical judgment.",
        "prefix": "ఆరోగ్య సహాయకం:",
    },
}


class ChatbotService:
    def __init__(self, rag_service: RAGService | None = None, memory_service: MemoryService | None = None, copilot_service: CopilotService | None = None) -> None:
        self.rag_service = rag_service or RAGService()
        self.memory_service = memory_service or MemoryService()
        self.copilot_service = copilot_service or CopilotService()

    def _authorize_patient_scope(self, current_user: User, patient_id: int | None) -> None:
        if current_user.role == UserRole.patient:
            if not current_user.patient_profile or (patient_id is not None and current_user.patient_profile.patient_id != patient_id):
                raise AppError("Access denied.", 403)

    def _authorize_session_access(self, current_user: User, session: ChatSession) -> None:
        if current_user.role == UserRole.patient:
            if not current_user.patient_profile or session.patient_id != current_user.patient_profile.patient_id:
                raise AppError("Access denied.", 403)

    def _session_title(self, audience: str, patient: Patient | None, message: str) -> str:
        base = patient.full_name if patient else audience.title()
        return f"{base} | {message[:48]}".rstrip()

    def _create_session(self, db: Session, current_user: User, payload: ChatRequest) -> ChatSession:
        patient = db.get(Patient, payload.patient_id) if payload.patient_id else current_user.patient_profile
        title = self._session_title(payload.audience, patient, payload.message)
        session = ChatSession(
            user_id=current_user.id,
            patient_id=patient.patient_id if patient else None,
            audience=payload.audience,
            language=payload.language,
            title=title,
            status="Active",
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    def _serialize_session(self, session: ChatSession) -> ChatSessionRead:
        return ChatSessionRead.model_validate(session)

    def _serialize_message(self, message: ChatMessage) -> ChatMessageRead:
        return ChatMessageRead.model_validate(message)

    def create_session(self, db: Session, current_user: User, payload: ChatSessionCreate) -> ChatSession:
        self._authorize_patient_scope(current_user, payload.patient_id)
        patient = db.get(Patient, payload.patient_id) if payload.patient_id else current_user.patient_profile
        session = ChatSession(
            user_id=current_user.id,
            patient_id=patient.patient_id if patient else None,
            audience=payload.audience,
            language=payload.language,
            title=payload.title,
            status="Active",
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    def list_sessions(self, db: Session, current_user: User) -> list[ChatSession]:
        stmt = select(ChatSession).order_by(ChatSession.last_message_at.desc().nullslast(), ChatSession.created_at.desc())
        if current_user.role == UserRole.patient and current_user.patient_profile:
            stmt = stmt.where(ChatSession.patient_id == current_user.patient_profile.patient_id)
        elif current_user.role in {UserRole.doctor, UserRole.staff, UserRole.admin}:
            pass
        else:
            stmt = stmt.where(ChatSession.user_id == current_user.id)
        return list(db.scalars(stmt).all())

    def list_messages(self, db: Session, current_user: User, session_id: int) -> list[ChatMessage]:
        session = db.get(ChatSession, session_id)
        if not session:
            raise AppError("Chat session not found.", 404)
        self._authorize_session_access(current_user, session)
        stmt = select(ChatMessage).where(ChatMessage.chat_session_id == session_id).order_by(ChatMessage.created_at.asc())
        return list(db.scalars(stmt).all())

    def _compose_response(self, db: Session, current_user: User, session: ChatSession, message: str) -> tuple[str, list[CitationRead], float]:
        audience = session.audience.lower()
        citations = []
        if audience in {"patient", "doctor", "admin", "staff"}:
            rag_hits = self.rag_service.search(db, message, top_k=4)
            citations = [
                CitationRead(
                    document_title=item.document_title,
                    source_type=item.source_type,
                    source_ref=item.source_ref,
                    chunk_index=item.chunk_index,
                    score=item.score,
                    excerpt=item.excerpt,
                )
                for item in rag_hits
            ]

        if audience == "doctor" and session.patient_id:
            summary = self.copilot_service.doctor_copilot(db, session.patient_id)
            response = f"{summary.title}\n{summary.summary}\nRecommendations: " + "; ".join(summary.recommendations)
            confidence = summary.confidence_score
        elif audience == "patient" and session.patient_id:
            summary = self.copilot_service.patient_assistant(db, session.patient_id)
            response = f"{summary.title}\n{summary.summary}\nRecommendations: " + "; ".join(summary.recommendations)
            confidence = summary.confidence_score
        elif audience == "admin":
            summary = self.copilot_service.admin_overview(db)
            response = f"{summary.title}\n{summary.summary}\nRecommendations: " + "; ".join(summary.recommendations)
            confidence = summary.confidence_score
        else:
            response = self._rag_response(message, citations)
            confidence = self._confidence_from_citations(citations, message)

        if citations and audience not in {"doctor", "patient", "admin"}:
            response = self._rag_response(message, citations)
        if not citations:
            response = f"I could not find a direct hospital knowledge match for '{message}'. {response}"
            confidence = min(confidence, 0.45)
        return response, citations, round(confidence, 2)

    def _confidence_from_citations(self, citations: list[CitationRead], message: str) -> float:
        base = 0.35
        if citations:
            base += min(0.45, citations[0].score * 0.5)
            base += min(0.15, len(citations) * 0.03)
        if len(message.split()) > 6:
            base += 0.05
        return min(base, 0.95)

    def _rag_response(self, message: str, citations: list[CitationRead]) -> str:
        if not citations:
            return "Please share more clinical context or upload relevant hospital knowledge so I can ground the answer."
        lead = citations[0]
        return (
            f"Based on hospital knowledge, the most relevant guidance comes from '{lead.document_title}'. "
            f"The strongest supporting excerpt is: {lead.excerpt[:220]}"
        )

    def send_message(self, db: Session, current_user: User, payload: ChatRequest) -> ChatResponse:
        if isinstance(payload, dict):
            payload = ChatRequest.model_validate(payload)
        self._authorize_patient_scope(current_user, payload.patient_id)
        session = db.get(ChatSession, payload.chat_session_id) if payload.chat_session_id else None
        if session is None:
            session = self._create_session(db, current_user, payload)
        else:
            self._authorize_session_access(current_user, session)

        user_message = ChatMessage(
            chat_session_id=session.chat_session_id,
            sender_role=current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role),
            content=payload.message,
            language=payload.language,
            confidence_score=1.0,
            citations={},
            metadata_json={"audience": payload.audience, "source": "user"},
        )
        db.add(user_message)
        db.flush()

        response_text, citations, confidence = self._compose_response(db, current_user, session, payload.message)
        translated_content = LANGUAGE_WRAPPERS.get(payload.language, {}).get("prefix")
        if translated_content:
            response_text = f"{translated_content} {response_text}"

        assistant_message = ChatMessage(
            chat_session_id=session.chat_session_id,
            sender_role="assistant",
            content=response_text,
            translated_content=response_text if payload.language != "English" else None,
            language=payload.language,
            confidence_score=confidence,
            citations={"items": [citation.model_dump() for citation in citations]},
            metadata_json={"audience": payload.audience, "source": "assistant", "language": payload.language},
        )
        db.add(assistant_message)

        session.last_message_at = datetime.now(timezone.utc)
        session.summary = response_text[:500]
        session.updated_at = datetime.now(timezone.utc)
        db.add(
            AuditLog(
                user_id=current_user.id,
                action="assistant_chat",
                entity_type="ChatSession",
                entity_id=str(session.chat_session_id),
                details={"audience": payload.audience, "language": payload.language, "message_length": len(payload.message)},
            )
        )
        memory_payload = {
            "last_query": payload.message,
            "last_response": response_text[:500],
            "confidence_score": confidence,
            "audience": payload.audience,
        }
        self.memory_service.upsert_memory(
            db,
            current_user,
            session.chat_session_id,
            memory_scope="conversation",
            memory_key="last_exchange",
            memory_value=memory_payload,
            patient_id=session.patient_id,
        )
        db.commit()
        db.refresh(session)
        db.refresh(user_message)
        db.refresh(assistant_message)

        safety_note = (
            LANGUAGE_WRAPPERS.get(payload.language, {}).get("disclaimer")
            or "AI-generated recommendations are intended to support healthcare professionals and should not replace clinical judgment."
        )

        return ChatResponse(
            chat_session=self._serialize_session(session),
            user_message=self._serialize_message(user_message),
            assistant_message=self._serialize_message(assistant_message),
            response=response_text,
            confidence_score=confidence,
            citations=citations,
            safety_note=safety_note,
            language=payload.language,
        )
