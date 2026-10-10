"""Panda verification mechanism: NLI-style answer verification with retry."""

import json
import re
from typing import Any, Callable, Dict, List, Optional

from src.agents.baselines.panda.types import VerificationResult


class PandaVerifier:
    """Verifies agent diagnosis against retrieved documents using NLI.

    Per the paper: the premise is the retrieved documents and tickets,
    NOT the tool execution results. The hypothesis is the proposed diagnosis.
    On failure, the agent should regenerate the answer (not gather more evidence).
    """

    def __init__(self, call_llm_fn: Callable, max_retries: int = 3):
        self._call_llm = call_llm_fn
        self.max_retries = max_retries
        self._attempt_count = 0

    @property
    def attempts_remaining(self) -> int:
        return max(0, self.max_retries - self._attempt_count)

    def reset(self):
        """Reset attempt counter for a new diagnosis cycle."""
        self._attempt_count = 0

    def verify(
        self,
        diagnosis: str,
        retrieved_docs: List[str],
    ) -> VerificationResult:
        """Verify whether retrieved documents support the diagnosis.

        Paper: "premise = retrieved documents and tickets, hypothesis = generated answer"

        Args:
            diagnosis: The proposed root cause / recommendation (hypothesis).
            retrieved_docs: Retrieved troubleshooting documents (the premise).
        """
        self._attempt_count += 1
        premise = self._format_premise(retrieved_docs)
        prompt = self._build_verification_prompt(premise, diagnosis)

        messages = [
            {"role": "system", "content": VERIFIER_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]
        raw_response = self._call_llm(messages)
        return self._parse_response(raw_response)

    def _format_premise(self, retrieved_docs: List[str]) -> str:
        """Format retrieved docs into a premise string.

        Paper: premise consists only of retrieved documents and tickets.
        """
        parts = []
        if retrieved_docs:
            parts.append("### Retrieved Documents")
            for i, doc in enumerate(retrieved_docs[:3], 1):
                parts.append(f"[Doc {i}]: {doc}")
        return "\n".join(parts) if parts else "No documents retrieved."

    def _build_verification_prompt(self, premise: str, hypothesis: str) -> str:
        """Build the NLI verification prompt."""
        return (
            f"## Evidence (Premise)\n{premise}\n\n"
            f"## Proposed Diagnosis (Hypothesis)\n{hypothesis}\n\n"
            "Classify the relationship as ACCEPT, REJECT, or NEUTRAL.\n"
            "- ACCEPT: the evidence clearly supports the diagnosis\n"
            "- REJECT: the evidence contradicts the diagnosis\n"
            "- NEUTRAL: insufficient evidence to determine\n"
            'Respond in JSON: {{"verdict": "accept|reject|neutral", "reasoning": "..."}}'
        )

    def _parse_response(self, raw_response: str) -> VerificationResult:
        """Parse LLM response into a VerificationResult."""
        try:
            match = re.search(r"\{[^}]+\}", raw_response, re.DOTALL)
            if match:
                data = json.loads(match.group())
                verdict = data.get("verdict", "neutral").lower().strip()
                if verdict not in ("accept", "reject", "neutral"):
                    verdict = "neutral"
                return VerificationResult(
                    verdict=verdict,
                    confidence=float(data.get("confidence", 0.5)),
                    reasoning=data.get("reasoning", ""),
                )
        except (json.JSONDecodeError, ValueError):
            pass
        lower = raw_response.lower()
        if "accept" in lower:
            return VerificationResult(verdict="accept", confidence=0.6)
        elif "reject" in lower:
            return VerificationResult(verdict="reject", confidence=0.6)
        return VerificationResult(verdict="neutral", confidence=0.3)


VERIFIER_SYSTEM_PROMPT = """You are a verification agent for database diagnosis.
Your task is to determine whether collected evidence logically supports a proposed diagnosis.
Classify as ACCEPT (evidence supports), REJECT (evidence refutes), or NEUTRAL (insufficient evidence).
Be strict: only classify as ACCEPT if the evidence clearly demonstrates the root cause.
Respond in JSON format: {"verdict": "accept|reject|neutral", "reasoning": "..."}"""


class PandaSourceAttribution:
    """Sentence-level source attribution for Panda's output.

    Paper: "Panda splits the output and the reference passages in individual
    sentences and provides inline citation if the output sentences are taken
    verbatim from the reference passages."
    """

    def __init__(self, similarity_threshold: float = 0.9):
        self._threshold = similarity_threshold
        self._model = None
        self._use_embeddings = False
        self._try_init_embeddings()

    def _try_init_embeddings(self):
        """Try to initialize sentence-transformers for semantic matching."""
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer("all-MiniLM-L6-v2")
            self._use_embeddings = True
        except (ImportError, Exception):
            self._use_embeddings = False

    def attribute(self, output_text: str, source_docs: List[str]) -> str:
        """Add inline citations to output text based on source documents.

        Returns the output text with [s_N] citations appended to sentences
        that are supported by source documents.
        """
        if not source_docs:
            return output_text

        output_sentences = self._split_sentences(output_text)
        source_sentences = []
        source_map = {}  # sentence -> (doc_index, sentence)
        for doc_idx, doc in enumerate(source_docs):
            for sent in self._split_sentences(doc):
                source_sentences.append(sent)
                source_map[sent] = doc_idx + 1

        if not output_sentences or not source_sentences:
            return output_text

        if self._use_embeddings:
            return self._attribute_by_embedding(
                output_text, output_sentences, source_sentences, source_map
            )
        return self._attribute_by_overlap(
            output_text, output_sentences, source_sentences, source_map
        )

    def _attribute_by_embedding(
        self,
        output_text: str,
        output_sentences: List[str],
        source_sentences: List[str],
        source_map: Dict[str, int],
    ) -> str:
        """Embedding-based semantic similarity attribution."""
        import numpy as np
        out_embs = self._model.encode(output_sentences, normalize_embeddings=True)
        src_embs = self._model.encode(source_sentences, normalize_embeddings=True)
        sim_matrix = np.dot(out_embs, src_embs.T)

        cited_output = output_text
        citations_used = set()
        for i, out_sent in enumerate(output_sentences):
            best_idx = int(np.argmax(sim_matrix[i]))
            best_score = sim_matrix[i][best_idx]
            if best_score >= self._threshold:
                src_sent = source_sentences[best_idx]
                doc_idx = source_map.get(src_sent, 0)
                if doc_idx > 0:
                    citation = f"[s{doc_idx}]"
                    citations_used.add(doc_idx)
                    cited_output = cited_output.replace(
                        out_sent, f"{out_sent}{citation}", 1
                    )
        return cited_output

    def _attribute_by_overlap(
        self,
        output_text: str,
        output_sentences: List[str],
        source_sentences: List[str],
        source_map: Dict[str, int],
    ) -> str:
        """Word-overlap based attribution fallback."""
        cited_output = output_text
        for out_sent in output_sentences:
            out_words = set(out_sent.lower().split())
            if len(out_words) < 4:
                continue
            best_score = 0.0
            best_doc_idx = 0
            for src_sent in source_sentences:
                src_words = set(src_sent.lower().split())
                if not src_words:
                    continue
                overlap = len(out_words & src_words) / max(len(out_words), 1)
                if overlap > best_score:
                    best_score = overlap
                    best_doc_idx = source_map.get(src_sent, 0)
            if best_score >= self._threshold and best_doc_idx > 0:
                citation = f"[s{best_doc_idx}]"
                cited_output = cited_output.replace(
                    out_sent, f"{out_sent}{citation}", 1
                )
        return cited_output

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        return [s.strip() for s in sentences if len(s.strip()) > 10]
