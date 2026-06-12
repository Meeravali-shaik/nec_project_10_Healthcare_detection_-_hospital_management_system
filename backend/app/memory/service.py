from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.assistant import AssistantMemory, ChatMessage, ChatSession
from app.models.user import User


class MemoryService:
    def get_session_memory(self, db: Session, session_id: int) -> list[AssistantMemory]:
        stmt = select(AssistantMemory).where(AssistantMemory.chat_session_id == session_id).order_by(AssistantMemory.updated_at.desc())
        return list(db.scalars(stmt).all())

    def upsert_memory(
        self,
        db: Session,
        current_user: User,
        session_id: int | None,
        memory_scope: str,
        memory_key: str,
        memory_value: dict,
        patient_id: int | None = None,
        ttl_hours: int = 72,
    ) -> AssistantMemory:
        expires_at = datetime.now(timezone.utc) + timedelta(hours=ttl_hours)
        stmt = select(AssistantMemory).where(
            AssistantMemory.user_id == current_user.id,
            AssistantMemory.chat_session_id == session_id,
            AssistantMemory.memory_scope == memory_scope,
            AssistantMemory.memory_key == memory_key,
        )
        memory = db.scalar(stmt)
        if memory:
            memory.memory_value = memory_value
            memory.patient_id = patient_id
            memory.expires_at = expires_at
        else:
            memory = AssistantMemory(
                user_id=current_user.id,
                patient_id=patient_id,
                chat_session_id=session_id,
                memory_scope=memory_scope,
                memory_key=memory_key,
                memory_value=memory_value,
                expires_at=expires_at,
            )
            db.add(memory)
        db.commit()
        db.refresh(memory)
        return memory

    def prune_expired(self, db: Session) -> int:
        result = db.execute(delete(AssistantMemory).where(AssistantMemory.expires_at.is_not(None), AssistantMemory.expires_at < datetime.now(timezone.utc)))
        db.commit()
        return int(result.rowcount or 0)

    def recent_messages(self, db: Session, session_id: int, limit: int = 6) -> list[ChatMessage]:
        stmt = select(ChatMessage).where(ChatMessage.chat_session_id == session_id).order_by(ChatMessage.created_at.desc()).limit(limit)
        return list(db.scalars(stmt).all())

    def get_session(self, db: Session, session_id: int) -> ChatSession | None:
        return db.get(ChatSession, session_id)

