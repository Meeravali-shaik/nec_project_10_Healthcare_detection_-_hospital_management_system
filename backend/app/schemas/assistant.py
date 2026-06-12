from datetime import datetime

from pydantic import Field

from app.schemas.common import ORMBaseModel


class ChatSessionCreate(ORMBaseModel):
    patient_id: int | None = None
    audience: str
    language: str = "English"
    title: str


class ChatSessionRead(ChatSessionCreate):
    chat_session_id: int
    user_id: int
    summary: str | None = None
    status: str
    last_message_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class ChatMessageCreate(ORMBaseModel):
    chat_session_id: int
    sender_role: str
    content: str
    language: str = "English"
    translated_content: str | None = None
    confidence_score: float = 0.0
    citations: dict = Field(default_factory=dict)
    metadata_json: dict = Field(default_factory=dict)


class ChatMessageRead(ChatMessageCreate):
    chat_message_id: int
    created_at: datetime


class ChatRequest(ORMBaseModel):
    chat_session_id: int | None = None
    audience: str
    language: str = "English"
    patient_id: int | None = None
    message: str


class CitationRead(ORMBaseModel):
    document_title: str
    source_type: str
    source_ref: str | None = None
    chunk_index: int
    score: float
    excerpt: str


class ChatResponse(ORMBaseModel):
    chat_session: ChatSessionRead
    user_message: ChatMessageRead
    assistant_message: ChatMessageRead
    response: str
    confidence_score: float
    citations: list[CitationRead] = Field(default_factory=list)
    safety_note: str
    language: str


class KnowledgeDocumentCreate(ORMBaseModel):
    title: str
    source_type: str
    source_ref: str | None = None
    language: str = "English"
    content: str
    summary: str | None = None
    tags: dict = Field(default_factory=dict)


class KnowledgeDocumentRead(ORMBaseModel):
    knowledge_document_id: int
    title: str
    source_type: str
    source_ref: str | None = None
    language: str
    summary: str | None = None
    tags: dict
    content_hash: str | None = None
    created_at: datetime
    updated_at: datetime


class KnowledgeSearchRequest(ORMBaseModel):
    query: str
    top_k: int = 5


class KnowledgeSearchResult(ORMBaseModel):
    document_title: str
    source_type: str
    source_ref: str | None = None
    chunk_index: int
    score: float
    excerpt: str
    metadata: dict = Field(default_factory=dict)


class InsightReportCreate(ORMBaseModel):
    report_type: str
    title: str
    summary: str
    narrative: str
    metrics_json: dict = Field(default_factory=dict)
    audience: str
    patient_id: int | None = None


class InsightReportRead(InsightReportCreate):
    insight_report_id: int
    created_by: int | None = None
    created_at: datetime


class GeneratedReportCreate(ORMBaseModel):
    report_type: str
    format: str = "PDF"
    title: str
    summary: str
    metadata_json: dict = Field(default_factory=dict)
    patient_id: int | None = None


class GeneratedReportRead(GeneratedReportCreate):
    generated_report_id: int
    file_name: str
    output_path: str
    created_by: int | None = None
    created_at: datetime


class AssistantMemoryRead(ORMBaseModel):
    assistant_memory_id: int
    user_id: int
    patient_id: int | None = None
    chat_session_id: int | None = None
    memory_scope: str
    memory_key: str
    memory_value: dict
    expires_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class NotificationTemplateCreate(ORMBaseModel):
    template_name: str
    audience: str
    channel: str
    language: str = "English"
    subject_template: str
    body_template: str
    metadata_json: dict = Field(default_factory=dict)


class NotificationTemplateRead(NotificationTemplateCreate):
    notification_template_id: int
    created_at: datetime


class ExecutiveInsightSummary(ORMBaseModel):
    occupancy_trend: str
    resource_utilization: str
    disease_trend: str
    revenue_trend: str
    staff_performance: str
    confidence_score: float
    narrative: str


class CopilotSummary(ORMBaseModel):
    audience: str
    title: str
    summary: str
    recommendations: list[str] = Field(default_factory=list)
    citations: list[CitationRead] = Field(default_factory=list)
    confidence_score: float = 0.0

