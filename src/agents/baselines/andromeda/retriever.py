"""Andromeda document retrieval module.

Implements the Heterogeneous Document Retrieval from the paper:
- Encodes user question into dense vector
- Retrieves top-k similar historical Q&A pairs
- Retrieves top-k relevant manual sections
- Uses sentence-transformers as the encoder (replacing paper's
  contrastive-learned model since original weights are unavailable)
"""

import logging
import os
from dataclasses import dataclass
from typing import List, Optional

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class RetrievedDocument:
    """A retrieved document from the knowledge base."""

    content: str
    source: str
    doc_type: str  # "historical_qa" or "manual"
    score: float = 0.0


class AndromedaRetriever:
    """Dense retrieval for Andromeda's multi-source evidence.

    Corresponds to the paper's Document Encoder that maps user questions,
    historical Q&A, and manual sections into a unified vector space.
    """

    def __init__(
        self,
        model_name: str = "BAAI/bge-base-en-v1.5",
        knowledge_dir: Optional[str] = None,
        top_k: int = 5,
    ):
        self.model_name = model_name
        self.top_k = top_k
        self._model = None
        self._documents: List[RetrievedDocument] = []
        self._embeddings: Optional[np.ndarray] = None

        if knowledge_dir:
            self.load_knowledge(knowledge_dir)

    def _get_model(self):
        """Lazy-load the sentence-transformers model."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                if not os.environ.get("HF_ENDPOINT"):
                    os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
                self._model = SentenceTransformer(self.model_name)
                logger.info(f"Loaded retrieval model: {self.model_name}")
            except ImportError:
                logger.warning(
                    "sentence-transformers not installed. "
                    "Falling back to keyword matching."
                )
                self._model = "fallback"
            except Exception as e:
                logger.warning(
                    f"Failed to load model {self.model_name}: {e}. "
                    "Falling back to keyword matching."
                )
                self._model = "fallback"
        return self._model

    def load_knowledge(self, knowledge_dir: str) -> None:
        """Load knowledge base from directory structure.

        Expected layout:
            knowledge_dir/
                pg_manual/       -> manual sections
                historical_qa/   -> Q&A pairs
        """
        self._documents = []
        self._embeddings = None

        manual_dir = os.path.join(knowledge_dir, "pg_manual")
        qa_dir = os.path.join(knowledge_dir, "historical_qa")

        if os.path.isdir(manual_dir):
            self._load_dir(manual_dir, "manual")
        if os.path.isdir(qa_dir):
            self._load_dir(qa_dir, "historical_qa")

        if not os.path.isdir(manual_dir) and not os.path.isdir(qa_dir):
            self._load_dir(knowledge_dir, "manual")

        logger.info(f"Loaded {len(self._documents)} documents from {knowledge_dir}")

    def _load_dir(self, dir_path: str, doc_type: str) -> None:
        """Load all .md/.txt files from a directory as documents."""
        if not os.path.isdir(dir_path):
            return
        for fname in sorted(os.listdir(dir_path)):
            if not fname.endswith((".md", ".txt")):
                continue
            fpath = os.path.join(dir_path, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()
            except (IOError, UnicodeDecodeError):
                continue
            chunks = self._chunk_document(content)
            for chunk in chunks:
                self._documents.append(RetrievedDocument(
                    content=chunk,
                    source=fname,
                    doc_type=doc_type,
                ))

    def _chunk_document(self, text: str, max_chars: int = 500) -> List[str]:
        """Split document into chunks by paragraph boundaries."""
        paragraphs = text.split("\n\n")
        chunks = []
        current = ""
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            if len(current) + len(para) > max_chars and current:
                chunks.append(current.strip())
                current = para
            else:
                current += "\n\n" + para if current else para
        if current.strip():
            chunks.append(current.strip())
        return chunks if chunks else [text[:max_chars]]

    def retrieve(self, query: str) -> List[RetrievedDocument]:
        """Retrieve top-k relevant documents for a query.

        Paper: encodes query and documents into unified vector space,
        retrieves by cosine similarity.
        """
        if not self._documents:
            return []

        model = self._get_model()
        if model == "fallback":
            return self._keyword_retrieve(query)

        return self._dense_retrieve(query, model)

    def retrieve_by_type(
        self, query: str, doc_type: str
    ) -> List[RetrievedDocument]:
        """Retrieve documents filtered by type (historical_qa or manual)."""
        all_results = self.retrieve(query)
        return [d for d in all_results if d.doc_type == doc_type]

    def rank_telemetry_texts(
        self, alert: str, telemetry_texts: List[str]
    ) -> List[str]:
        """Rank telemetry anomaly descriptions by relevance to alert.

        Paper Section 2.1: Relevant Telemetry Selection — rank anomalous
        descriptions by semantic similarity to the user's NL question.
        """
        if not telemetry_texts:
            return []

        model = self._get_model()
        if model == "fallback":
            return telemetry_texts

        alert_emb = model.encode([alert], normalize_embeddings=True)
        text_embs = model.encode(telemetry_texts, normalize_embeddings=True)
        scores = np.dot(text_embs, alert_emb.T).flatten()
        ranked_indices = np.argsort(scores)[::-1]
        return [telemetry_texts[i] for i in ranked_indices]

    def _dense_retrieve(self, query: str, model) -> List[RetrievedDocument]:
        """Dense retrieval using sentence-transformers."""
        if self._embeddings is None:
            texts = [d.content for d in self._documents]
            self._embeddings = model.encode(texts, normalize_embeddings=True)

        query_emb = model.encode([query], normalize_embeddings=True)
        scores = np.dot(self._embeddings, query_emb.T).flatten()
        top_indices = np.argsort(scores)[::-1][: self.top_k]

        results = []
        for idx in top_indices:
            doc = self._documents[idx]
            results.append(RetrievedDocument(
                content=doc.content,
                source=doc.source,
                doc_type=doc.doc_type,
                score=float(scores[idx]),
            ))
        return results

    def _keyword_retrieve(self, query: str) -> List[RetrievedDocument]:
        """Fallback keyword-based retrieval when no embedding model."""
        keywords = set(query.lower().split())
        scored = []
        for doc in self._documents:
            content_lower = doc.content.lower()
            score = sum(1 for kw in keywords if kw in content_lower)
            if score > 0:
                scored.append((score / max(len(keywords), 1), doc))
        scored.sort(key=lambda x: x[0], reverse=True)
        results = []
        for score, doc in scored[: self.top_k]:
            results.append(RetrievedDocument(
                content=doc.content,
                source=doc.source,
                doc_type=doc.doc_type,
                score=score,
            ))
        return results