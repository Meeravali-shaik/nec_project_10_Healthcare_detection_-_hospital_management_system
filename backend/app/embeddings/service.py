from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class VectorSearchResult:
    score: float
    text: str
    metadata: dict[str, Any]


class EmbeddingService:
    def __init__(self, store_dir: str | Path = "vector_store", model_name: str = "tfidf-baseline") -> None:
        self.store_dir = Path(store_dir)
        self.model_name = model_name
        self.store_dir.mkdir(parents=True, exist_ok=True)

    def chunk_text(self, text: str, chunk_size: int = 140, overlap: int = 20) -> list[str]:
        words = text.split()
        if not words:
            return []
        chunks: list[str] = []
        start = 0
        while start < len(words):
            end = min(len(words), start + chunk_size)
            chunks.append(" ".join(words[start:end]))
            if end == len(words):
                break
            start = max(end - overlap, start + 1)
        return chunks

    def _artifact_path(self, collection_name: str) -> Path:
        safe_name = collection_name.replace("/", "_").replace("\\", "_")
        return self.store_dir / f"{safe_name}.joblib"

    def build_index(self, collection_name: str, documents: list[dict[str, Any]]) -> dict[str, Any]:
        texts = [doc["text"] for doc in documents]
        if not texts:
            artifact = {"vectorizer": None, "matrix": None, "documents": [], "model_name": self.model_name}
            joblib.dump(artifact, self._artifact_path(collection_name))
            return artifact

        vectorizer = TfidfVectorizer(stop_words="english")
        matrix = vectorizer.fit_transform(texts)
        artifact = {
            "vectorizer": vectorizer,
            "matrix": matrix,
            "documents": documents,
            "model_name": self.model_name,
        }
        joblib.dump(artifact, self._artifact_path(collection_name))
        return artifact

    def load_index(self, collection_name: str) -> dict[str, Any] | None:
        path = self._artifact_path(collection_name)
        if not path.exists():
            return None
        return joblib.load(path)

    def search(self, collection_name: str, query: str, top_k: int = 5) -> list[VectorSearchResult]:
        artifact = self.load_index(collection_name)
        if not artifact or not artifact.get("vectorizer") or artifact.get("matrix") is None:
            return []

        vectorizer: TfidfVectorizer = artifact["vectorizer"]
        matrix = artifact["matrix"]
        documents = artifact["documents"]
        query_vector = vectorizer.transform([query])
        scores = cosine_similarity(query_vector, matrix).ravel()
        ranked_indexes = np.argsort(scores)[::-1][:top_k]
        results: list[VectorSearchResult] = []
        for index in ranked_indexes:
            score = float(scores[index])
            if score <= 0:
                continue
            doc = documents[index]
            results.append(VectorSearchResult(score=round(score, 4), text=doc["text"], metadata=doc.get("metadata", {})))
        return results

