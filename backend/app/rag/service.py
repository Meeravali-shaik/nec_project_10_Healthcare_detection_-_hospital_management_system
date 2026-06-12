from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime, timezone
from hashlib import sha256

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.embeddings.service import EmbeddingService
from app.models.assistant import DocumentChunk, EmbeddingRecord, KnowledgeDocument
from app.models.ai import AuditLog
from app.models.user import User
from app.schemas.assistant import KnowledgeDocumentCreate, KnowledgeSearchResult


class RAGService:
    collection_name = "hospital_knowledge_base"

    def __init__(self, embedding_service: EmbeddingService | None = None) -> None:
        self.embedding_service = embedding_service or EmbeddingService()

    def _chunk_payloads(self, document: KnowledgeDocument, chunks: Iterable[DocumentChunk]) -> list[dict]:
        payloads: list[dict] = []
        for chunk in chunks:
            payloads.append(
                {
                    "id": chunk.document_chunk_id,
                    "text": chunk.chunk_text,
                    "metadata": {
                        "document_id": document.knowledge_document_id,
                        "document_title": document.title,
                        "source_type": document.source_type,
                        "source_ref": document.source_ref,
                        "language": document.language,
                        "chunk_index": chunk.chunk_index,
                        "metadata": chunk.metadata_json,
                    },
                }
            )
        return payloads

    def _log(self, db: Session, current_user: User | None, action: str, details: dict) -> None:
        db.add(
            AuditLog(
                user_id=current_user.id if current_user else None,
                action=action,
                entity_type="KnowledgeDocument",
                entity_id=details.get("knowledge_document_id"),
                details=details,
            )
        )

    def ingest_document(self, db: Session, current_user: User | None, payload: KnowledgeDocumentCreate) -> KnowledgeDocument:
        content = payload.content.strip()
        content_hash = sha256(content.encode("utf-8")).hexdigest()
        existing = db.scalar(select(KnowledgeDocument).where(KnowledgeDocument.content_hash == content_hash))
        if existing:
            document = existing
            document.summary = payload.summary or document.summary
            document.tags = payload.tags
            document.updated_at = datetime.now(timezone.utc)
            db.query(EmbeddingRecord).filter(EmbeddingRecord.knowledge_document_id == document.knowledge_document_id).delete(synchronize_session=False)
            db.query(DocumentChunk).filter(DocumentChunk.knowledge_document_id == document.knowledge_document_id).delete(synchronize_session=False)
        else:
            document = KnowledgeDocument(
                title=payload.title,
                source_type=payload.source_type,
                source_ref=payload.source_ref,
                language=payload.language,
                summary=payload.summary,
                tags=payload.tags,
                content_hash=content_hash,
                uploaded_by=current_user.id if current_user else None,
            )
            db.add(document)
            db.flush()

        chunks = self.embedding_service.chunk_text(content)
        chunk_rows: list[DocumentChunk] = []
        for index, chunk_text in enumerate(chunks):
            chunk_row = DocumentChunk(
                knowledge_document_id=document.knowledge_document_id,
                chunk_index=index,
                chunk_text=chunk_text,
                token_count=len(chunk_text.split()),
                metadata_json={"title": payload.title, "source_type": payload.source_type},
            )
            db.add(chunk_row)
            chunk_rows.append(chunk_row)

        db.flush()
        for chunk_row in chunk_rows:
            db.add(
                EmbeddingRecord(
                    knowledge_document_id=document.knowledge_document_id,
                    document_chunk_id=chunk_row.document_chunk_id,
                    vector_store="tfidf",
                    model_name=self.embedding_service.model_name,
                    embedding_dimension=len(chunks),
                    confidence_score=1.0,
                    metadata_json={"chunk_index": chunk_row.chunk_index},
                )
            )

        db.commit()
        db.refresh(document)
        self.refresh_index(db)
        self._log(db, current_user, "ingest_knowledge_document", {"knowledge_document_id": document.knowledge_document_id, "title": document.title})
        db.commit()
        return document

    def refresh_index(self, db: Session) -> dict:
        documents = list(
            db.execute(
                select(KnowledgeDocument, DocumentChunk)
                .join(DocumentChunk, DocumentChunk.knowledge_document_id == KnowledgeDocument.knowledge_document_id)
                .order_by(KnowledgeDocument.knowledge_document_id.asc(), DocumentChunk.chunk_index.asc())
            ).all()
        )
        payloads = []
        for document, chunk in documents:
            payloads.extend(self._chunk_payloads(document, [chunk]))
        return self.embedding_service.build_index(self.collection_name, payloads)

    def search(self, db: Session, query: str, top_k: int = 5) -> list[KnowledgeSearchResult]:
        if not self.embedding_service.load_index(self.collection_name):
            self.refresh_index(db)
        results = self.embedding_service.search(self.collection_name, query, top_k=top_k)
        return [
            KnowledgeSearchResult(
                document_title=result.metadata.get("document_title", "Unknown"),
                source_type=result.metadata.get("source_type", "Unknown"),
                source_ref=result.metadata.get("source_ref"),
                chunk_index=int(result.metadata.get("chunk_index", 0)),
                score=result.score,
                excerpt=result.text[:500],
                metadata=result.metadata,
            )
            for result in results
        ]
