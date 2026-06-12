# Phase 5 Architecture

## Backend Modules

- `app/models/assistant.py`
- `app/schemas/assistant.py`
- `app/embeddings/service.py`
- `app/rag/service.py`
- `app/chatbot/service.py`
- `app/copilots/service.py`
- `app/memory/service.py`
- `app/insights/service.py`
- `app/ai_reports/service.py`
- `app/api/routes/assistant.py`

## Database Models

- `ChatSession`
- `ChatMessage`
- `KnowledgeDocument`
- `DocumentChunk`
- `EmbeddingRecord`
- `InsightReport`
- `GeneratedReport`
- `AssistantMemory`
- `NotificationTemplate`

## AI / RAG Design

- TF-IDF-based embedding pipeline with persisted local vector artifacts.
- Retrieval-Augmented Generation grounded in hospital documents and patient context.
- Role-aware response generation for patients, doctors, admins, and staff.
- Confidence scoring based on retrieval quality and context depth.
- Citation support returned alongside every assistant answer.

## APIs

- `POST /api/v1/assistant/chat`
- `POST /api/v1/assistant/sessions`
- `GET /api/v1/assistant/sessions`
- `GET /api/v1/assistant/sessions/{id}/messages`
- `POST /api/v1/assistant/knowledge`
- `POST /api/v1/assistant/knowledge/search`
- `GET /api/v1/assistant/copilots/patient/{patient_id}`
- `GET /api/v1/assistant/copilots/doctor/{patient_id}`
- `GET /api/v1/assistant/insights/executive`
- `POST /api/v1/assistant/reports`

## Frontend Pages

- `/assistant`
- `/assistant/chat`
- `/assistant/patient`
- `/assistant/doctor`
- `/assistant/knowledge`
- `/assistant/insights`
- `/assistant/reports`

## Testing Strategy

- Chatbot service tests
- RAG retrieval tests
- report generation tests
- security and role-scope tests
- integration tests over assistant routes

## Deployment Strategy

- Persist vector artifacts in a mounted volume.
- Keep generated reports in durable storage.
- Use PostgreSQL for production databases.
- Run ingestion and embedding refresh jobs as background or scheduled tasks.

