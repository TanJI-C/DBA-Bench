"""Panda feedback mechanism: vector-store cache for learning from past interactions.

Paper: "Panda achieves this by requesting the user to provide a binary feedback
in terms of 'Helpful' or 'Not Helpful' for each generated response. This feedback
along with the user query and its response are stored in a vector store indexed
by the vector embedding of the user query."

"Panda retrieves at-least 1 and at-most 3 responses of both positive and negative feedback."
"""

from typing import Any, Dict, List, Optional

from src.agents.baselines.panda.types import FeedbackEntry


class PandaFeedbackStore:
    """Stores query-action-observation triples with feedback labels.

    Uses embedding-based retrieval (with keyword fallback) and distinguishes
    positive/negative feedback per the paper's design.
    """

    def __init__(self, max_entries: int = 50):
        self._entries: List[FeedbackEntry] = []
        self._max_entries = max_entries
        self._model = None
        self._embeddings: List[Any] = []
        self._use_embeddings = False
        self._try_init_embeddings()

    def _try_init_embeddings(self):
        """Try to initialize sentence-transformers for embedding-based retrieval."""
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer("all-MiniLM-L6-v2")
            self._use_embeddings = True
        except (ImportError, Exception):
            self._use_embeddings = False

    def store(self, entry: FeedbackEntry):
        """Store a feedback entry with its embedding."""
        self._entries.append(entry)
        if self._use_embeddings and self._model:
            text = entry.query + " " + " ".join(entry.observations[:2])
            emb = self._model.encode([text], normalize_embeddings=True)
            self._embeddings.append(emb[0])
        if len(self._entries) > self._max_entries:
            self._entries.pop(0)
            if self._embeddings:
                self._embeddings.pop(0)

    def store_interaction(
        self,
        query: str,
        actions: List[Dict[str, Any]],
        observations: List[str],
        outcome: str = "",
    ):
        """Convenience method to store an interaction."""
        self.store(FeedbackEntry(
            query=query,
            actions_taken=actions,
            observations=observations,
            outcome=outcome,
        ))

    def retrieve_similar(self, query: str, top_k: int = 3) -> List[str]:
        """Retrieve similar past interactions using embedding similarity.

        Paper: "retrieves at-least 1 and at-most 3 responses of both positive
        and negative feedback"
        """
        if not self._entries:
            return []
        if self._use_embeddings and self._model and self._embeddings:
            return self._retrieve_by_embedding(query, top_k)
        return self._retrieve_by_keyword(query, top_k)

    def _retrieve_by_embedding(self, query: str, top_k: int) -> List[str]:
        """Embedding-based cosine similarity retrieval."""
        import numpy as np
        query_emb = self._model.encode([query], normalize_embeddings=True)
        emb_matrix = np.array(self._embeddings)
        scores = np.dot(emb_matrix, query_emb.T).flatten()
        top_indices = np.argsort(scores)[::-1]

        # Paper: retrieve both positive and negative feedback
        positive = []
        negative = []
        for idx in top_indices:
            if scores[idx] < 0.1:
                break
            entry = self._entries[idx]
            formatted = self._format_entry(entry)
            if entry.outcome in ("success", "helpful"):
                if len(positive) < top_k:
                    positive.append(f"[POSITIVE] {formatted}")
            elif entry.outcome in ("failure", "not_helpful"):
                if len(negative) < top_k:
                    negative.append(f"[NEGATIVE] {formatted}")
            else:
                if len(positive) < top_k:
                    positive.append(formatted)
            if len(positive) + len(negative) >= top_k * 2:
                break
        # Paper: at least 1 and at most 3 of each
        results = positive[:top_k] + negative[:top_k]
        return results[:top_k * 2]

    def _retrieve_by_keyword(self, query: str, top_k: int) -> List[str]:
        """Keyword-based fallback retrieval."""
        stop_words = {"the", "is", "a", "an", "in", "on", "of", "to", "for",
                      "and", "or", "it", "this", "that", "are", "was", "be"}
        keywords = set(query.lower().split()) - stop_words
        if not keywords:
            keywords = set(query.lower().split())
        scored = []
        for entry in self._entries:
            entry_text = entry.query + " ".join(entry.observations)
            entry_words = set(entry_text.lower().split())
            overlap = len(keywords & entry_words)
            if overlap > 0:
                scored.append((overlap, entry))
        scored.sort(key=lambda x: x[0], reverse=True)

        results = []
        for _, entry in scored[:top_k]:
            formatted = self._format_entry(entry)
            if entry.outcome in ("failure", "not_helpful"):
                results.append(f"[NEGATIVE] {formatted}")
            elif entry.outcome in ("success", "helpful"):
                results.append(f"[POSITIVE] {formatted}")
            else:
                results.append(formatted)
        return results

    def get_recent(self, n: int = 3) -> List[str]:
        """Get the N most recent interactions as formatted text."""
        recent = self._entries[-n:] if self._entries else []
        return [self._format_entry(e) for e in recent]

    def _format_entry(self, entry: FeedbackEntry) -> str:
        """Format a feedback entry as text for prompt inclusion."""
        parts = [f"Query: {entry.query}"]
        if entry.actions_taken:
            actions_str = ", ".join(
                a.get("api", "unknown") for a in entry.actions_taken
            )
            parts.append(f"Actions: {actions_str}")
        if entry.observations:
            parts.append(f"Observations: {entry.observations[-1][:200]}")
        if entry.outcome:
            parts.append(f"Outcome: {entry.outcome}")
        return " | ".join(parts)

    @property
    def size(self) -> int:
        return len(self._entries)
