"""DBAIOps prompt templates - Paper Section 6.2.

Structured prompts: prompt = ⟨Sa, Sl, Sm, Se, So⟩
"""

DBAIOPS_SYSTEM_PROMPT = """You are an expert database administrator performing root cause analysis.
You have access to a knowledge graph of O&M experience and collected diagnostic evidence.
Analyze the provided information following established database principles and generate
a structured diagnosis report.
If you finish by calling `submit()` with an explicit `report` object, the report must
follow the evaluation schema exactly (no extra or missing fields):
{"diagnosis": {"conditions": [{"type": str, "factor": str, "entity": str, "evidence": [str]}]},
 "outcome": {"changes": [str], "verification": [str]},
 "summary": str}
`summary` is a top-level string; `outcome.plan` is optional."""

DBAIOPS_DIAGNOSIS_PROMPT = """## Anomaly Description (Sa)
{anomaly_description}

## Detection Condition (Sl)
{detection_condition}

## Metric Statistics & ADF Evidence (Sm)
{metrics_summary}

## O&M Experience from Knowledge Graph (Se)
{experience_paths}

## Required Output Format (So)
Generate a diagnosis report with the following sections:

1. **Anomaly Validation**: Determine whether this anomaly requires further investigation.
   State whether the evidence confirms a real issue.

2. **Root Cause Analysis**: Identify up to 5 likely root causes, each supported by
   specific metrics, logs, or known fault signatures from the provided evidence.
   Rank them by likelihood.

3. **Recovery Solution**: For each identified root cause, suggest specific technical
   adjustments (configuration changes, query optimizations, resource scaling, etc.).

4. **Summary**: Provide a concise assessment of overall system health and urgency.

5. **SQL Context**: Include any relevant SQL statements or execution plans if the
   issue involves database operations.

IMPORTANT: Only cite metrics and evidence that appear in the provided data above.
Do not hallucinate or fabricate metric values."""

DBAIOPS_REMEDIATION_PROMPT = """## Anomaly Description
{anomaly_description}

## Detection Condition
{detection_condition}

## Anomaly Detection Verdict
{anomaly_verdict}

## Metric Statistics & ADF Evidence
{metric_evidence}

## Collected Observations (raw, truncated)
{metrics_summary}

## O&M Experience from Knowledge Graph
{experience_paths}

## Task
Based on the evidence above, diagnose the root cause and FIX it by calling
the appropriate tools. After applying the fix, verify it worked (e.g. re-check
metrics or re-run the problematic query). Once verified, call `submit()` to
finish.

Do NOT just describe the fix — actually execute it via tool calls."""

DBAIOPS_FALLBACK_PROMPT = """The knowledge graph has no trigger vertex matching this alert.
Investigate the alert with your available tools (metrics, SQL, logs), identify the root
cause, and FIX it by calling the appropriate tools. Once the remediation is applied and
verified, call `submit()` to finish.

Alert: {alert}

Observations so far:
{observations}"""
