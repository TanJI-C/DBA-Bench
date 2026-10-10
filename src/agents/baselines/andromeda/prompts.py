"""Andromeda baseline prompt templates.

Implements the two-phase configuration reasoning prompts
as described in the Andromeda paper (SIGMOD 2025).
"""

SYSTEM_PROMPT = """\
You are Andromeda, an expert database performance debugging system.
Your task is to diagnose DBMS configuration issues and recommend specific \
configuration knob adjustments based on the provided evidence.

You follow a structured two-phase reasoning process:
- Phase 1: Identify which configuration knobs are relevant to the problem
- Phase 2: Recommend specific values for each identified knob

You base your reasoning on:
1. Anomalous telemetry data (metrics showing abnormal behavior)
2. Retrieved historical questions and solutions from similar problems
3. Relevant DBMS manual sections describing configuration parameters
4. Execution logs and current configuration state
"""

PHASE1_KNOB_IDENTIFICATION_PROMPT = """\
## Task: Configuration Knob Identification (Phase 1)

Given the following evidence about a database performance issue, identify \
which DBMS configuration knobs are most likely related to the problem.

### Problem Description
{alert_text}

### Anomalous Telemetry Data
{telemetry_text}

### Retrieved Historical Questions (similar problems and their solutions)
{historical_qa_text}

### Retrieved Manual Sections (relevant configuration documentation)
{manual_text}

### Execution Logs
{log_text}

### Instructions
Based on ALL the evidence above, identify the configuration knobs that are \
most likely causing or contributing to this performance issue.

Respond in the following JSON format:
```json
{{
  "reasoning": "Step-by-step analysis of how the evidence points to specific knobs",
  "knobs": ["knob_name_1", "knob_name_2", ...],
  "confidence": 0.0-1.0
}}
```
"""

PHASE2_VALUE_RECOMMENDATION_PROMPT = """\
## Task: Configuration Value Recommendation (Phase 2)

You have identified the following configuration knobs as relevant to the \
database performance issue. Now recommend specific values for each knob.

### Problem Description
{alert_text}

### Identified Knobs (from Phase 1)
{phase1_knobs}

### Current Configuration Values
{current_config}

### Anomalous Telemetry Data
{telemetry_text}

### Retrieved Evidence (historical solutions + manual sections)
{evidence_text}

### Instructions
For each identified knob, recommend a specific value that would resolve or \
mitigate the performance issue. Base your recommendations on the evidence.

Respond in the following JSON format:
```json
{{
  "root_cause": "Concise description of the root cause",
  "recommendations": [
    {{
      "knob": "knob_name",
      "current_value": "current",
      "recommended_value": "recommended",
      "rationale": "Why this change helps"
    }}
  ]
}}
```
"""

TELEMETRY_TEXT_TEMPLATE = (
    "Metric '{metric_name}' is anomalous{timestamp_part}: "
    "observed value {value:.4g}, "
    "expected range [{low:.4g}, {high:.4g}], "
    "{direction} normal by {severity:.1f} standard deviations."
)

NO_ANOMALY_TEXT = "No significant anomalies detected in the collected telemetry data."

NO_EVIDENCE_TEXT = "No relevant historical questions or manual sections found."