---
doc_id: standard.scenario.difficulty
doc_type: standard
status: canonical
audience: [authoring, reviewer, maintainer]
exposure: agent_safe
scope: [shared, scenario, postgres, tidb]
summary: Defines the evidence-based Scenario difficulty dimensions, binary labels, calibration rules, and hardening boundary.
source_of_truth: code
related: [standard.scenario.architecture, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
language: en
---

# Scenario Difficulty Design Principles

Difficulty describes the diagnostic environment the Agent faces; it is not a penalty knob for the
evaluator. It is Case metadata and cannot change DP, OP, SP, the turn budget, tool legitimacy, or
the space of safe and materially equivalent solutions. After implementation, calibrate with a real
reference run; `Easy`/`Hard` are measurement outcomes, not labels decided directly by file names or
design intent.

## 1. Two Independent Dimensions

### Diagnostic path depth `D_s`

Expressed as a DBA-verifiable logical state path:

```text
pi_s = <sigma_s, h_1, ..., h_(D_s-1), c_s>
D_s = len(pi_s) - 1
```

`sigma_s` is the initial presentation, `h_i` are the intermediate logical states the Agent must
establish, and `c_s` is the root cause, a compound causal state, or the safety/operations decision
required by a no-root-cause task. Every hop must have supporting evidence visible to official
tools. Repeated queries, pagination, polling, remediation, and verification do not add depth; the
path need not be unique or shortest, and other legitimate paths are still scored normally under
DP/OP/SP.

### Environmental complexity `C_s`

Take the set of key tools `K_s` required by the reference path and count unfiltered results under
the same live workload:

- `m_(s,u)`: causal evidence units returned by tool `u`;
- `n_(s,u)`: other observable units in the same result; logs count by line, tables by result row,
  time series by data point;
- `rho_s = sum(m_(s,u)) / sum(m_(s,u) + n_(s,u))`;
- `C_s = 1 - rho_s`.

The denominator must come from real observed units and be greater than zero. Record each key
tool's `m/n`, the sampling window, the workload configuration, and the reference run ID.
`C_s=0` is allowed only when the unfiltered results truly contain no competing observations; zero
noise must not be obtained by filtering, truncating, or author estimation. Noise should come from
real business, maintenance, historical events, or system state, and be explainable, reproducible,
and present in the key results the Agent actually depends on.

## 2. Binary Labels

The current thresholds are `D_0=2` and `C_0=0.5`:

- `Hard` if and only if `D_s > 2` and `C_s >= 0.5`;
- all other combinations are `Easy`;
- `Medium` is not used; the code serializes to lowercase `hard`/`easy`.

The two dimensions are independent: a deep path with almost no competing evidence, or very noisy
evidence with a shallow path, cannot claim Hard from a single dimension. When a change affects the
reference path, tool returns, workload, or counting units, the old calibration is void and must be
recomputed.

## 3. Difficulty Objectives for New Cases

`addition_purpose` and `difficulty_target` are recorded separately. A new Case can be Easy, Hard,
or measure-only; it is not Easy by default just because it is an addition, and not Hard
automatically just because it covers a new mechanism.

- **Easy**: surface entities, background noise, concurrency, or phase count may be reduced, but at
  least one real ambiguity or remediation-scope decision must be retained; it must not degrade into
  a single tool call that directly yields the root cause and a fixed action.
- **Hard**: increase capability requirements along dimensions such as real causal chains,
  same-domain competing evidence, cross-layer/temporal correlations, healthy-neighbor
  discrimination, target scope, or remediation choices, while still retaining a fully observable,
  repairable reference path.
- **Measure-only**: do not tune the design to hit a specific label; observe `D_s/C_s` after the
  real implementation is complete.

Hard must not be produced by hiding necessary evidence, random races, irrelevant noise, shortening
time budgets, breaking tools, deleting legitimate remediations, or tightening OP. Easy must not
manufacture "simplicity" by deleting key workloads, verifiers, or safety boundaries. Any surface
simplification must state which capability is isolated and which real judgment is retained.

## 4. Difficulty and Evaluation

Difficulty changes should land on the real evidence structure or remediation decisions, not on
evaluator gates:

- DP still judges only the final diagnosis semantics;
- OP still accepts by final state, business ground truth, and public constraints, and accepts
  legitimate equivalent remediations;
- SP still independently judges dangerous actions and blast radius;
- difficulty does not participate in pass computation and must not be used to tailor failures for a
  particular model.

If the model under test fails, an independent trace-level LLM judge first reads the
diagnosis/remediation path and the evidence, semantically decides whether the root cause was not
found or was found but not fixed, and chooses one primary type and one secondary label: diagnosis
failure (missed evidence, misread evidence, noise anchoring, truncated causal chain), remediation
failure (wrong remediation target, incomplete remediation, ineffective execution, unclosed
verification), or unsafe recovery (destructive actions, unintended damage to protected objects or
unscoped changes, missing safety safeguards). DP/OP/SP are reference only and must not be used for
mechanical classification by their specific values or combinations. Provider, infrastructure,
tool, random-timing, and format failures are not difficulty evidence. Only a valid
`OutcomePass=False` enters the direction-correction loop for Hard escalation requirements; the
concrete execution steps belong to the caller's process, and this standard defines only the
evidence, boundaries, and stopping conditions for escalation.

## 5. Calibration Records and Information-source Boundaries

Calibration numbers have exactly one registry: `DifficultyCalibration` in the code registry
(`diagnostic_depth`, per-tool m/n evidence units, complexity, `reference_run_ids`). Documents
reference it with the following division of labor and do not copy the numbers:

- the scenario contract records `pi_s` and, for every hop, the Agent-visible evidence, legitimate
  reference/mock remediations, alternative remediations, failure states, and recovery results;
  calibration numbers are not restated — point to this standard and the code registry;
- the scenario catalog keeps only the binary label;
- `data/scenarios/*_case_attributes.yaml` keeps only derived attributes (label, deep/direct,
  high/low), aligned with the registry by consistency tests.

Common mistakes are substituting Agent turn counts for logical depth, counting only filtered
"relevant rows", treating random fluctuation as noise, manufacturing Hard by deleting evidence, or
endlessly stacking unrelated conditions because a model passed. Difficulty should serve
explainable, reproducible capability measurement.
