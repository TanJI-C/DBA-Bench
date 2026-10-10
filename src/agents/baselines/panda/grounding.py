"""Panda grounding mechanism: Document Retriever + Telemetry-to-Text + Context Aggregator."""

import json
import math
import os
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple

from src.agents.baselines.panda.types import GroundingContext, TelemetryFeature
from src.agents.baselines.telemetry import ParsedMetricSeries


@dataclass
class KnowledgeSnippet:
    content: str
    source: str
    relevance: float = 0.0


class PandaDocumentRetriever:
    """Embedding-based RAG over troubleshooting docs with keyword fallback."""

    def __init__(
        self,
        paths: Optional[List[str]] = None,
        top_k: int = 3,
        chunk_size: int = 500,
        relevance_threshold: float = 0.85,
    ):
        self.top_k = top_k
        self.chunk_size = chunk_size
        self.relevance_threshold = relevance_threshold
        self.snippets: List[KnowledgeSnippet] = []
        self._embeddings: Optional[Any] = None
        self._model: Optional[Any] = None
        self._use_embeddings = False

        if paths:
            self._load_paths(paths)
            self._try_init_embeddings()

    def _try_init_embeddings(self):
        """Try to initialize sentence-transformers for embedding-based retrieval."""
        if not self.snippets:
            return
        try:
            from sentence_transformers import SentenceTransformer
            import numpy as np
            self._model = SentenceTransformer("all-MiniLM-L6-v2")
            texts = [s.content for s in self.snippets]
            self._embeddings = self._model.encode(texts, normalize_embeddings=True)
            self._use_embeddings = True
        except (ImportError, Exception):
            self._use_embeddings = False

    def _load_paths(self, paths: List[str]):
        """Load knowledge from file paths."""
        for path in paths:
            if not os.path.exists(path):
                continue
            if os.path.isfile(path):
                self._load_file(path)
            elif os.path.isdir(path):
                for fname in sorted(os.listdir(path)):
                    fpath = os.path.join(path, fname)
                    if os.path.isfile(fpath) and fname.endswith((".txt", ".md")):
                        self._load_file(fpath)

    def _load_file(self, path: str):
        """Load a single file as knowledge snippets."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            for chunk in self._chunk_text(content):
                self.snippets.append(KnowledgeSnippet(content=chunk, source=path))
        except (IOError, UnicodeDecodeError):
            pass

    def _chunk_text(self, text: str) -> List[str]:
        """Split text into chunks by paragraph boundaries."""
        paragraphs = text.split("\n\n")
        chunks = []
        current = ""
        for para in paragraphs:
            if len(current) + len(para) > self.chunk_size and current:
                chunks.append(current.strip())
                current = para
            else:
                current += "\n\n" + para if current else para
        if current.strip():
            chunks.append(current.strip())
        return chunks

    def retrieve(self, query: str) -> List[KnowledgeSnippet]:
        """Retrieve relevant snippets for a query."""
        if not self.snippets:
            return []
        if self._use_embeddings:
            return self._retrieve_by_embedding(query)
        return self._retrieve_by_keyword(query)

    def _retrieve_by_embedding(self, query: str) -> List[KnowledgeSnippet]:
        """Embedding-based cosine similarity retrieval."""
        import numpy as np
        query_emb = self._model.encode([query], normalize_embeddings=True)
        scores = np.dot(self._embeddings, query_emb.T).flatten()
        top_indices = np.argsort(scores)[::-1][: self.top_k]
        results = []
        for idx in top_indices:
            if scores[idx] >= self.relevance_threshold:
                snippet = self.snippets[idx]
                snippet.relevance = float(scores[idx])
                results.append(snippet)
        return results

    def _retrieve_by_keyword(self, query: str) -> List[KnowledgeSnippet]:
        """Keyword-based fallback retrieval."""
        keywords = set(query.lower().split())
        scored = []
        for snippet in self.snippets:
            content_lower = snippet.content.lower()
            score = sum(1 for kw in keywords if kw in content_lower)
            if score > 0:
                scored.append((score, snippet))
        scored.sort(key=lambda x: x[0], reverse=True)
        results = []
        for score, snippet in scored[: self.top_k]:
            snippet.relevance = score / max(len(keywords), 1)
            results.append(snippet)
        return results


class PandaTelemetryToText:
    """Converts raw metric values to interpretable text features.

    Implements Panda's Telemetry-to-Text (T2T) mechanism:
    trend detection, change point detection, statistics, seasonality,
    cross-metric correlation, and anomalous metric identification.
    """

    def __init__(self):
        self._all_series: Dict[str, Any] = {}

    def extract_features(self, metric_name: str, values: List[float]) -> TelemetryFeature:
        """Extract statistical features from a metric time series."""
        self._all_series[metric_name] = values
        if not values:
            return TelemetryFeature(
                metric_name=metric_name, trend="unknown", mean=0.0, p95=0.0,
                text_summary=f"{metric_name}: no data available",
            )
        mean_val = sum(values) / len(values)
        p95_val = self._percentile(values, 0.95)
        trend = self._detect_trend(values)
        change_points = self._detect_change_points(values)
        seasonality = self._detect_seasonality(values)

        feature = TelemetryFeature(
            metric_name=metric_name,
            trend=trend,
            mean=mean_val,
            p95=p95_val,
            change_points=change_points,
            seasonality=seasonality,
        )
        feature.text_summary = self._to_text(feature)
        return feature

    def extract_series_features(self, series: List[ParsedMetricSeries] | tuple[ParsedMetricSeries, ...]) -> List[TelemetryFeature]:
        features = []
        for parsed in series:
            feature_name = f"{parsed.metric}[{parsed.series_target}].{parsed.field}"
            self._all_series[feature_name] = (parsed.timestamps_ms, parsed.values)
            feature = self.extract_features(feature_name, list(parsed.values))
            self._all_series[feature_name] = (parsed.timestamps_ms, parsed.values)
            features.append(feature)
        return features

    def compute_correlations(self, features: List[TelemetryFeature]) -> List[TelemetryFeature]:
        """Compute pairwise correlations between all collected metrics.

        Paper: "extract interpretable features like trend, seasonality, mean, p95,
        and correlation score for each metric"
        """
        names = [f.metric_name for f in features]
        for feature in features:
            series_a = self._series_data(self._all_series.get(feature.metric_name))
            if not series_a[1]:
                continue
            for other_name in names:
                if other_name == feature.metric_name:
                    continue
                series_b = self._series_data(self._all_series.get(other_name))
                if not series_b[1]:
                    continue
                corr = self._pearson_correlation_aligned(series_a, series_b)
                if abs(corr) > 0.5:
                    feature.correlation_with[other_name] = round(corr, 3)
            feature.text_summary = self._to_text(feature)
        return features

    @staticmethod
    def _series_data(value: Any) -> Tuple[Optional[Dict[int, float]], List[float]]:
        if isinstance(value, tuple) and len(value) == 2:
            timestamps, values = value
            return dict(zip(timestamps, values, strict=True)), list(values)
        return None, list(value or [])

    def _pearson_correlation_aligned(
        self,
        left: Tuple[Optional[Dict[int, float]], List[float]],
        right: Tuple[Optional[Dict[int, float]], List[float]],
    ) -> float:
        if left[0] is not None and right[0] is not None:
            common = sorted(set(left[0]) & set(right[0]))
            if not common:
                raise ValueError("Panda telemetry correlation has no common timestamps")
            return self._pearson_correlation([left[0][timestamp] for timestamp in common], [right[0][timestamp] for timestamp in common])
        return self._pearson_correlation(left[1], right[1])

    def identify_problematic_metrics(
        self, features: List[TelemetryFeature]
    ) -> Tuple[List[TelemetryFeature], List[str]]:
        """Identify which metrics are anomalous.

        Paper: "Panda uses these features to identify problematic metrics."
        A metric is problematic if it has:
        - An increasing/decreasing trend, OR
        - One or more change points, OR
        - High p95 relative to mean (spike indicator)
        """
        problematic = []
        summaries = []
        for f in features:
            is_problematic = False
            reasons = []
            if f.trend in ("increasing", "decreasing"):
                is_problematic = True
                reasons.append(f"trend={f.trend}")
            if f.change_points:
                is_problematic = True
                reasons.append(f"{len(f.change_points)} change point(s)")
            if f.mean > 0 and f.p95 / f.mean > 2.0:
                is_problematic = True
                reasons.append(f"p95/mean ratio={f.p95/f.mean:.1f}")
            if f.correlation_with:
                correlated = [
                    f"{k}(r={v:.2f})" for k, v in f.correlation_with.items()
                    if abs(v) > 0.7
                ]
                if correlated:
                    reasons.append(f"correlated with {', '.join(correlated)}")
            if is_problematic:
                problematic.append(f)
                summaries.append(
                    f"[ANOMALY] {f.metric_name}: {', '.join(reasons)}"
                )
        return problematic, summaries

    def _detect_trend(self, values: List[float]) -> str:
        """Detect trend by comparing first-half mean to second-half mean."""
        n = len(values)
        if n < 4:
            return "stable"
        mid = n // 2
        first_half_mean = sum(values[:mid]) / mid
        second_half_mean = sum(values[mid:]) / (n - mid)
        overall_mean = sum(values) / n
        if overall_mean == 0:
            return "stable"
        relative_change = (second_half_mean - first_half_mean) / max(abs(overall_mean), 1e-9)
        if relative_change > 0.15:
            return "increasing"
        elif relative_change < -0.15:
            return "decreasing"
        return "stable"

    def _detect_change_points(self, values: List[float], window: int = 5) -> List[int]:
        """Detect change points using rolling mean comparison."""
        if len(values) < window * 2:
            return []
        change_points = []
        overall_std = self._std(values)
        if overall_std == 0:
            return []
        threshold = 1.5 * overall_std
        for i in range(window, len(values) - window):
            left_mean = sum(values[i - window:i]) / window
            right_mean = sum(values[i:i + window]) / window
            if abs(right_mean - left_mean) >= threshold:
                if not change_points or i - change_points[-1] >= window:
                    change_points.append(i)
        return change_points

    def _detect_seasonality(self, values: List[float], max_lag: int = 20) -> bool:
        """Detect seasonality via autocorrelation."""
        n = len(values)
        if n < max_lag * 2:
            return False
        mean_val = sum(values) / n
        variance = sum((v - mean_val) ** 2 for v in values) / n
        if variance == 0:
            return False
        for lag in range(2, min(max_lag, n // 2)):
            autocorr = sum(
                (values[i] - mean_val) * (values[i + lag] - mean_val)
                for i in range(n - lag)
            ) / ((n - lag) * variance)
            if autocorr > 0.7:
                return True
        return False

    def _percentile(self, values: List[float], p: float) -> float:
        """Compute percentile."""
        sorted_vals = sorted(values)
        idx = int(p * (len(sorted_vals) - 1))
        return sorted_vals[idx]

    def _std(self, values: List[float]) -> float:
        """Compute standard deviation."""
        if len(values) < 2:
            return 0.0
        mean_val = sum(values) / len(values)
        variance = sum((v - mean_val) ** 2 for v in values) / len(values)
        return math.sqrt(variance)

    def _to_text(self, feature: TelemetryFeature) -> str:
        """Convert a TelemetryFeature to natural language text."""
        parts = [
            f"{feature.metric_name}:",
            f"trend={feature.trend},",
            f"mean={feature.mean:.2f},",
            f"p95={feature.p95:.2f},",
            f"{len(feature.change_points)} change point(s) detected,",
            f"seasonal={'yes' if feature.seasonality else 'no'}",
        ]
        if feature.correlation_with:
            corr_strs = [f"{k}(r={v:.2f})" for k, v in feature.correlation_with.items()]
            parts.append(f"correlated with: {', '.join(corr_strs)}")
        return " ".join(parts)

    def _pearson_correlation(self, a: List[float], b: List[float]) -> float:
        """Compute Pearson correlation between two series (truncated to same length)."""
        n = min(len(a), len(b))
        if n < 3:
            return 0.0
        a, b = a[:n], b[:n]
        mean_a = sum(a) / n
        mean_b = sum(b) / n
        cov = sum((a[i] - mean_a) * (b[i] - mean_b) for i in range(n)) / n
        std_a = math.sqrt(sum((x - mean_a) ** 2 for x in a) / n)
        std_b = math.sqrt(sum((x - mean_b) ** 2 for x in b) / n)
        if std_a == 0 or std_b == 0:
            return 0.0
        return cov / (std_a * std_b)


class PandaContextAggregator:
    """Combines docs + telemetry text + schema into structured JSON prompt."""

    def aggregate(
        self,
        alert: str,
        documents: List[KnowledgeSnippet],
        telemetry_features: List[TelemetryFeature],
        schema_info: str = "",
        feedback_examples: List[str] = None,
    ) -> GroundingContext:
        """Build a GroundingContext from all sources."""
        doc_texts = [s.content for s in documents]
        telemetry_texts = [f.text_summary for f in telemetry_features]

        context_obj = {
            "alert": alert,
            "telemetry_analysis": telemetry_texts,
            "relevant_documents": doc_texts[:3],
            "schema_context": schema_info,
            "previous_interactions": feedback_examples or [],
        }
        aggregated = json.dumps(context_obj, indent=2, ensure_ascii=False)

        return GroundingContext(
            documents=doc_texts,
            telemetry_text=telemetry_texts,
            schema_info=schema_info,
            aggregated_prompt=aggregated,
        )
