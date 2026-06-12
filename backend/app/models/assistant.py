from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    chat_session_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    patient_id: Mapped[int | None] = mapped_column(ForeignKey("patients.patient_id"), nullable=True, index=True)
    audience: Mapped[str] = mapped_column(String(50), nullable=False)
    language: Mapped[str] = mapped_column(String(50), default="English", nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="Active", nullable=False)
    last_message_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user = relationship("User")
    patient = relationship("Patient")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")
    memories = relationship("AssistantMemory", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    chat_message_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    chat_session_id: Mapped[int] = mapped_column(ForeignKey("chat_sessions.chat_session_id"), nullable=False, index=True)
    sender_role: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    translated_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    language: Mapped[str] = mapped_column(String(50), default="English", nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    citations: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    metadata_json: Mapped[dict] = mapped_column("metadata", JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    session = relationship("ChatSession", back_populates="messages")


class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"

    knowledge_document_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(String(100), nullable=False)
    source_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    language: Mapped[str] = mapped_column(String(50), default="English", nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    content_hash: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    uploaded_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    uploader = relationship("User")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    embeddings = relationship("EmbeddingRecord", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    document_chunk_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    knowledge_document_id: Mapped[int] = mapped_column(ForeignKey("knowledge_documents.knowledge_document_id"), nullable=False, index=True)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    metadata_json: Mapped[dict] = mapped_column("metadata", JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    document = relationship("KnowledgeDocument", back_populates="chunks")
    embeddings = relationship("EmbeddingRecord", back_populates="chunk", cascade="all, delete-orphan")


class EmbeddingRecord(Base):
    __tablename__ = "embedding_records"

    embedding_record_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    knowledge_document_id: Mapped[int] = mapped_column(ForeignKey("knowledge_documents.knowledge_document_id"), nullable=False, index=True)
    document_chunk_id: Mapped[int | None] = mapped_column(ForeignKey("document_chunks.document_chunk_id"), nullable=True, index=True)
    vector_store: Mapped[str] = mapped_column(String(100), default="tfidf", nullable=False)
    model_name: Mapped[str] = mapped_column(String(100), default="tfidf-baseline", nullable=False)
    embedding_dimension: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    metadata_json: Mapped[dict] = mapped_column("metadata", JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    document = relationship("KnowledgeDocument", back_populates="embeddings")
    chunk = relationship("DocumentChunk", back_populates="embeddings")


class InsightReport(Base):
    __tablename__ = "insight_reports"

    insight_report_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    report_type: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    narrative: Mapped[str] = mapped_column(Text, nullable=False)
    metrics_json: Mapped[dict] = mapped_column("metrics", JSON, default=dict, nullable=False)
    audience: Mapped[str] = mapped_column(String(50), nullable=False)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    patient_id: Mapped[int | None] = mapped_column(ForeignKey("patients.patient_id"), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


class GeneratedReport(Base):
    __tablename__ = "generated_reports"

    generated_report_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    report_type: Mapped[str] = mapped_column(String(100), nullable=False)
    format: Mapped[str] = mapped_column(String(20), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    output_path: Mapped[str] = mapped_column(String(500), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[dict] = mapped_column("metadata", JSON, default=dict, nullable=False)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


class AssistantMemory(Base):
    __tablename__ = "assistant_memory"

    assistant_memory_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    patient_id: Mapped[int | None] = mapped_column(ForeignKey("patients.patient_id"), nullable=True, index=True)
    chat_session_id: Mapped[int | None] = mapped_column(ForeignKey("chat_sessions.chat_session_id"), nullable=True, index=True)
    memory_scope: Mapped[str] = mapped_column(String(50), nullable=False)
    memory_key: Mapped[str] = mapped_column(String(100), nullable=False)
    memory_value: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    session = relationship("ChatSession", back_populates="memories")
    user = relationship("User")
    patient = relationship("Patient")


class NotificationTemplate(Base):
    __tablename__ = "notification_templates"

    notification_template_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    template_name: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    audience: Mapped[str] = mapped_column(String(50), nullable=False)
    channel: Mapped[str] = mapped_column(String(50), nullable=False)
    language: Mapped[str] = mapped_column(String(50), default="English", nullable=False)
    subject_template: Mapped[str] = mapped_column(String(255), nullable=False)
    body_template: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[dict] = mapped_column("metadata", JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
