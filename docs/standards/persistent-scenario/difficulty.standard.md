---
doc_id: standard.persistent-scenario.difficulty
doc_type: standard
status: canonical
audience: [authoring, reviewer, maintainer]
exposure: agent_safe
scope: [shared, persistent-scenario, postgres, tidb]
summary: Defines difficulty through production decisions, recurrence and whole-system reference, no-action and wrong-action paths.
source_of_truth: contract
related: [standard.persistent-scenario.architecture, standard.persistent-scenario.evaluation, standard.scenario.difficulty, guide.persistent-scenario.implement-persistent-scenario]
language: en
---

# Persistent Scenario Difficulty and Three-path Calibration

## 1. Scope

This standard applies to production-oriented OLTP, OLAP, and HTAP continuous operations; see the
companion [evaluation standard](evaluation.standard.md). It replaces the practice of deriving
long-task difficulty from case composition, event counts, and per-event solvability.

## 2. Capability Under Test

Difficulty comes from real business trade-offs, causal decoupling, discovery paths, cross-time
state retention, and recurrence prevention. It does not come from severity, event counts, fixed
remediation deadlines, or amplified losses. alert/inspection, high noise, and long duration are
instance properties and are not, on their own, sufficient to make distinct production services.

## 3. The Three Paths Are Required Evidence

The full-handling path proves that the end-to-end business and safety contracts can be satisfied
with public tools and accepts equivalent remediations; zero-handling proves that governance is
needed and cannot rely on all faults persisting forever; wrong-handling proves that superficial
recovery, one-sided optimization, and dangerous shortcuts can be rejected.

The three paths validate the whole system; per-case solvability must not substitute for combined
solvability. One action clearing two faults, a third fault eliminating the second symptom, and
early protection preventing recurrence must all have legitimate evaluations. If zero action still
passes all business contracts, the instance must be re-reviewed rather than forcibly adding events
to close the requirement.

## 4. Difficulty Evidence

Keep interpretable vectors: business service conflicts, shared resources, causal masking, incident
discovery opportunities, effective remediation choices, recurrence mechanisms, context, and
persistent state. Record real arrivals, business losses, prevention, recovery, and side effects;
do not use an all-event closure rate as a difficulty score.

Repeating the same mechanism can measure recurrence prevention and continued learning; control
differences in business volume, cache, data, and fault intensity, and compare paired losses with
handling evidence — a single faster second round does not prove learning. Clearing sessions or
revoking protections that have already taken effect in order to manufacture difficulty is
forbidden.

## 5. Calibration Order

Static and resource admission -> repeated healthy normal/peak load -> zero handling -> full
handling and equivalent solutions -> wrong handling -> unresolved/resolved/prevented combination
prefixes -> cleanup/ledger integrity -> real-model repeated pilots.

Thresholds are frozen based on business commitments and resource feasibility and must not be tuned
back based on model failures. Without reliable evidence, keep measure-only/development_provisional;
Hard requires a repeatable, attributable decision-capability gap. Hard must not be created by
shrinking budgets, hiding normal operations evidence, or compressing response deadlines.

## 6. Formal Evidence

Preserve input seeds, data/topology/resource/code/spec versions, three-path traces, observability
and ledger validity, model repetition results, the invalid list, cleanup, and threshold provenance.
Business delivery deadlines may affect business outcomes; the author's fault-remediation deadline
is response observation only. Report DP/OP/SP separately; do not compute an overall pass or count
invalid runs as model failures.
