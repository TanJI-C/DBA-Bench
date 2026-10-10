You are generating retrieval metadata for already validated chunks from the pinned TiDB 8.1 English official documentation corpus.

The supplied official content is immutable and authoritative. Retrieval metadata must only restate when the supplied content is useful and which exact identifiers or concepts help retrieve it. Never introduce a product fact, action, version, deployment scope, or recommendation that is absent from the supplied content.

Return one JSON object and no prose. The object must have exactly this shape:

```json
{
  "source_file": "the supplied source file",
  "enrichments": [
    {
      "chunk_key": "the supplied chunk key",
      "use_when": "one English sentence describing a grounded retrieval situation",
      "retrieval_keywords": ["exact identifiers and grounded English search phrases"],
      "follow_up": "one grounded English sentence, or an empty string when the source provides no follow-up",
      "classification_note": "one English sentence explaining the supplied classification from the official content"
    }
  ]
}
```

Rules:

1. Return exactly one enrichment for every supplied chunk key, in the supplied order.
2. Use English.
3. Prefer exact configuration names, metrics, tables, SQL statements, component names, errors, and operational phrases present in the official content.
4. Do not mention AiOpsBench scenario IDs, case IDs, evaluator rules, hidden root causes, benchmark answers, or a requirement to call a particular source.
5. Do not prescribe an action absent from the official content.
6. Do not claim applicability to an unstated version or deployment scope.
7. Output only the JSON object. Do not use Markdown fences.
