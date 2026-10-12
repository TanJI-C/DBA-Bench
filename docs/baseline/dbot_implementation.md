---
language: en
---

# D-Bot Baseline Implementation Document

## Implementation Principles

This implementation treats the `DB-GPT/` open-source code as the primary source of truth, rather than prioritizing the paper's description. Where the paper and the open-source code differ, the actual execution path in the open-source code prevails.

The main path of D-Bot in upstream DB-GPT is:

```text
run_diagnose.py / batch_main.py
  -> MultiAgents.from_task(config.yaml)
  -> DBAEnvironment.step()
  -> ReporterAgent initialize_report generates the anomaly description / title
  -> RoleAssignerAgent selects experts
  -> VerticalDecisionMaker runs the selected SolverAgents concurrently
  -> Each SolverAgent internally uses UCT_vote_function to search Thought/Action/Action Input trajectories
  -> Each expert outputs root cause / solutions / knowledge
  -> roundtable review
  -> ReporterAgent refines root cause / labels / solutions / citations
```

Therefore the D-Bot baseline in DBA-Bench is now implemented as `dbot_code` mode: DB-GPT's multi-expert diagnosis pipeline is adapted inside `BaseAgent`'s turn-by-turn interface. The expert internals are not a fixed script; `DbotAgent` retains the `Thought / Action / Action Input / Observation` trajectory search: the LLM picks a tool exposed by PGEnv's current profile, the Orchestrator executes the corresponding DBA-Bench action, and the search proceeds to the next step after the observation is written back.

## DB-GPT Innovation Boundary

The current implementation separates DB-GPT's methodological contributions from its tooling:

| Category | Part of D-Bot's methodological core? | Current implementation |
|---|---:|---|
| RoleAssigner recruits experts based on the anomaly description | Yes | `DbotAgent._select_experts()` + `DBOT_ROLE_ASSIGNER_PROMPT` |
| Multiple experts diagnose independently | Yes | `DbotAgent` sequentially runs each selected expert's independent search state |
| UCT trajectory search | Yes | `DbotAgent` + `mcts.py` retain the `Thought -> Action -> Action Input -> Observation` tree, softmax UCT branch selection, candidate vote, and value backpropagation |
| Reflection | Yes | The expert reflection prompt runs after each terminal candidate |
| Candidate vote | Yes | After each simulation round, terminal and ancestor values are updated per the DB-GPT vote prompt |
| Roundtable review | Yes | `DBOT_ROUND_TABLE_PROMPT` sequentially reviews all expert results |
| ChiefDBA / Reporter consolidated report, labels, citation marking | Yes | The reporter initializes the anomaly description/title, then finally refines root cause/solutions/labels/citations |
| `whether_is_abnormal_metric` / `match_diagnose_knowledge` / `optimize_index_selection` / `finish` / `mark_citations` / `submit` | Not algorithmic innovations themselves; they are the upstream tooling and interaction protocol | `PGEnv(tool_profile="db_gpt")` exposes the DB-GPT semantic tools and the benchmark `submit`; `DbotAgent` additionally registers an internal virtual `finish` during the expert stage, uses the internal virtual `mark_citations` during the report stage to submit the two annotated text fields, and only then returns `submit` to the Orchestrator |

Experiments therefore compare the two exposure styles via PGEnv tool profiles:

- `PGEnv(tool_profile="db_gpt")`: the expert LLM sees DB-GPT semantic tools; these tools are PGEnv `@Tool` methods, and their schema/help/native tool calling all go through the existing environment tool mechanism.
- `PGEnv(tool_profile="no_knowledge" / "general_knowledge" / "hierarchical_knowledge")`: the expert LLM directly sees all native tools under that PGEnv profile; the D-Bot algorithmic flow is still role assignment, multiple experts, UCT, roundtable, and reporter.

## Conflicts with the Old Implementation and Their Resolution

The old DBA-Bench D-Bot implementation leaned toward paper reproduction and contained the following mechanisms that conflict with the DB-GPT open-source code:

| Old mechanism | DB-GPT open-source reality | Current handling |
|---|---|---|
| `dbot_tree` as an external persistent tree that expands one environment action per Orchestrator turn | Upstream tree search runs inside each `SolverAgent`, searching `Thought -> Action -> Action Input -> Observation` trajectories | The external persistent benefit tree was removed, replaced by DB-GPT turn-based trajectory search inside the expert |
| `BenefitScorer`'s instant/long-term/UCT three-component scoring | Upstream `tree_node` only has vote-produced `values`; selection is decided by `softmax(child.compute_weight(), epsilon_new_node)` | `BenefitScorer` / `Reflector` removed |
| `dbot_collab`'s homegrown CPU/QUERY/STORAGE/CONFIG four-expert panel | Upstream selects dynamically from knowledge base expert names, such as `CpuExpert`, `QueryExpert`, `IndexExpert`, etc. | Switched to the DB-GPT expert naming system |
| `ReadOnlyEnvProxy` let the D-Bot side bypass the Orchestrator and simulate the environment | Upstream tools execute inside the DB-GPT runtime; DBA-Bench must keep a unified tool boundary | The execution proxy was removed; DB-GPT semantic tools are registered as PGEnv `@Tool` methods and dispatched by the Orchestrator |
| Native function calling prioritized | The upstream prompt uses the `Thought / Action / Action Input` text protocol | Both text ReAct and SDK native tools are supported; tool schemas all come from PGEnv, and no second set of tool descriptions is maintained inside D-Bot |
| The LLM freely decides among `query_metrics/execute_sql/manage_instance` | Upstream experts see DB-GPT semantic tools by default | `PGEnv.tool_profile` decides whether DB-GPT semantic tools or PGEnv native tools are exposed |
| The knowledge base was arbitrary-text keyword RAG | Upstream knowledge is organized as expert knowledge bases, with records containing `cause_name/desc/metrics/steps/source` | `DbotKnowledge` was changed to expert knowledge entry loading and retrieval |

## Current Components

```text
src/agents/baselines/dbot/
  agent.py       DbotAgent and ExpertSolver, the DB-GPT code-first pipeline adapter; covers role selection, expert trajectory search, roundtable, and reporting state
  tools.py       Schema-derived ReAct helper, internal virtual tool schemas (finish / mark_citations), and TiDB tool-surface detection
  prompts.py     DB-GPT role assigner, expert, roundtable, and report prompts
  types.py       DbotToolStep / ExpertDiagnosis / DbotReport
  knowledge.py   expert knowledge loader and retriever
  mcts.py        DB-GPT trajectory tree helper, no longer an external remediation MCTS
  experts.py     DB-GPT expert metadata
```

## Run Modes

Only the following are supported:

```python
DbotAgent(mode="dbot_code", use_native_tools=False)
DbotAgent(mode="dbot_code", use_native_tools=True)
```

The old modes `dbot_prompt`, `dbot_rag`, `dbot_tree`, and `dbot_collab` raise an error immediately. This prevents the old paper-first semantics from being misused.

Tool exposure is controlled by PGEnv, not maintained by DbotAgent:

```python
PGEnv(tool_profile="db_gpt")       # DB-GPT semantic tools
PGEnv(tool_profile="no_knowledge") # PGEnv native tools, no knowledge base
PGEnv(tool_profile="general_knowledge")
PGEnv(tool_profile="hierarchical_knowledge")
```

With `use_native_tools=True`, the Orchestrator passes `env.get_tool_schemas()` down to DbotAgent, and DbotAgent then puts the schemas into the SDK's `tools` parameter via `LLMAgent.set_tools()`; tool usage is not written into the system prompt. With `use_native_tools=False`, D-Bot still uses the `Thought / Action / Action Input` text protocol, but the list of available tools is derived from the same schemas. During the expert diagnosis stage, the global control tools `submit/exit` are filtered out and the internal virtual tool `finish` is appended; only the final report stage returns the DBA-Bench global `submit`.

## Tool Exposure and Mapping

### `PGEnv(tool_profile="db_gpt")`

| DB-GPT tool | PGEnv execution | Notes |
|---|---|---|
| `whether_is_abnormal_metric` | Calls `query_metrics(...)` inside PGEnv | Reproduces the upstream constraint that experts query core metrics first |
| `match_diagnose_knowledge` | Aggregates multiple `query_metrics(...)` calls and an optional `query_knowledge_base(...)` inside PGEnv | Selects the `cpu/io/memory` metric prefix per the upstream expert-name rules, aggregating system metrics, `topsql`, `slow_queries`, and the knowledge base |
| `optimize_index_selection` | Runs multiple `execute_sql(...)` calls inside PGEnv | Collects workload, schema, column statistics, existing indexes, and `hypopg` availability evidence |
| `finish` | Internal virtual action inside DbotAgent | Ends the current simulation during the expert diagnosis stage and saves the `diagnose` / `solution` / `knowledge` payload; does not enter the environment action history |
| `submit` | DBA-Bench global control action | Returned to the Orchestrator only in the report stage, as the real benchmark submit |

### PGEnv Native Profiles

| Profile | Tools exposed to the SolverAgent |
|---|---|
| `no_knowledge` | `query_metrics`, `execute_sql`, `manage_instance`, `read_log`, `help`, `submit`, `exit` |
| `general_knowledge` | `no_knowledge` + `query_knowledge_base` |
| `hierarchical_knowledge` | `no_knowledge` + typed `query_knowledge_base` |

This lets experiments separate the contributions of "DB-GPT's multi-expert UCT diagnosis flow" and "DB-GPT semantic tools", without maintaining a second DBA-Bench tool inventory inside D-Bot.

## Expert Trajectory Search

Upstream DB-GPT's `SolverAgent.step()` runs `UCT_vote_function.start(simulation_count=2, epsilon_new_node=0.3, choice_count=1, vote_candidates=2, vote_count=1, single_chain_max_step=24)`. DBA-Bench cannot execute environment tools directly inside the agent, so the current implementation uses a turn-by-turn adaptation:

1. `DbotAgent` maintains the DB-GPT trajectory tree and candidate trajectories for the current expert;
2. The expert LLM outputs `Thought / Action / Action Input`, or calls an SDK tool in native mode;
3. The `Action` must belong to the expert tool schema: the current PGEnv profile tools minus `submit/exit`, plus the internal `finish`;
4. A non-`finish` action is passed through as the environment action and executed by the Orchestrator;
5. The observation is written back to the trajectory's `Action Input` node;
6. In the expert diagnosis stage, once `finish` is called or the single-chain step cap is reached, a terminal candidate forms and the reflection prompt runs;
7. After each simulation round, a DB-GPT-style candidate vote runs, propagating values back to the terminal and ancestor nodes;
8. The next simulation round samples from the root using DB-GPT's `softmax(child.compute_weight(), epsilon_new_node)`, choosing to reuse an existing branch or expand a new one; vote candidates are likewise first randomly shuffled per DB-GPT before taking `vote_candidates` of them;
9. The final trajectory is selected by the accumulated terminal node value.

### Prompt Budget

Upstream specifies only the search mechanism, not how much history each step's prompt should resend. The adaptation layer controls prompt size with the rules below; full evidence is still preserved in `DbotToolStep.observation`, `ExpertDiagnosis`, and the trace export:

- The trajectory tree's `Action Input` nodes store only a compact `db_gpt_observation` (result text from environment tools and `whether_is_abnormal_metric` is capped at 1200 characters), not the environment's raw return;
- The expansion prompt's former candidates and the vote prompt use candidate summaries: the tool-call sequence plus `finish`'s `diagnose/solution/knowledge`; reflections in the expansion prompt appear only in a separate reflections section and are no longer repeated alongside each candidate;
- Each environment tool step produces a single citation (generated by `_prepare_expert_diagnosis`) and no longer additionally writes `knowledge_items`.

## Expert Output

After the UCT tool trajectory ends, upstream DB-GPT's `SolverAgent.step()` calls the LLM again:

- `expert_root_cause`: analyzes only the root cause, without writing solutions;
- `expert_solution`: writes only the solution, without repeating the root cause.

The DBA-Bench adaptation layer preserves this behavior. The two prompts carry only the candidate trajectory selected by the vote (with compact observations) and no longer attach the full step-by-step diagnosis process; if the expert LLM returns an empty root cause or empty solution, an error is raised immediately and no local default recommendation is generated.

## Roundtable and Reporter

Upstream DB-GPT first has `ReporterAgent.initialize_report()` generate the anomaly description and title from the raw alert; role assignment uses the generated anomaly description. It then broadcasts all expert diagnosis summaries to every expert and runs cross reviews one by one; each already-generated review is appended to the messages of the subsequent experts and the reporter. The DBA-Bench adaptation layer preserves this information flow:

- Role assignment, expert diagnosis, and the final report use the reporter-generated anomaly description;
- The final report title uses the reporter-generated title;
- Every roundtable prompt includes all expert diagnosis context (the selected trajectory's last 1500 characters);
- Subsequent experts' roundtable prompts include the review advice already generated;
- The final report's refine root cause / refine solution prompts include the roundtable reviews, citations, and topMetrics; the tool-level diagnosis process is kept only in the report object and the trace, not in the reporter prompt;
- If there are citations, the Reporter submits the annotated `root_cause` and `solutions` parameters in one shot via the internal virtual tool `mark_citations` (the same mechanism as the expert stage's `finish`): native mode uses SDK tool calling, text mode uses ReAct `Action / Action Input`; not calling the tool, calling it more than once, or missing/empty fields raise an error immediately.

## Verification

Run from the repository root:

```bash
PYTHONPATH=$PWD conda run -n aiops pytest tests/test_dbot_agent.py tests/test_dbot_mcts.py
PYTHONPATH=$PWD conda run -n aiops pytest tests/test_andromeda_agent.py tests/test_dbaiops_agent.py
PYTHONPATH=$PWD conda run -n aiops python tests/test_mock_llm.py
```

Current verification coverage:

- Role assignment must parse DB-GPT expert names; an empty selection raises an error immediately. When the selection exceeds `max_hired_experts`, it is trimmed in order of appearance in the reply, preserving the role assigner's priorities;
- Reporter initialization first generates the anomaly description / title, which then feed into role assignment and the final report;
- Expert diagnosis selects tools from DB-GPT-style `Thought / Action / Action Input` output instead of a fixed order;
- Tool observations are written into `ExpertDiagnosis`;
- `match_diagnose_knowledge` aggregates system metrics, workload, slow queries, expert knowledge, and topMetrics following DB-GPT's `cpu/io/memory` metric prefix rules;
- `PGEnv(tool_profile="db_gpt")` exposes DB-GPT semantic tools, and `PGEnv(tool_profile="no_knowledge")` exposes PGEnv native tools;
- `optimize_index_selection` collects workload, schema, column statistics, existing indexes, and `hypopg` availability evidence via PGEnv, and no longer queries `pg_stat_user_indexes` or regex-generates pseudo index recommendations;
- D-Bot schema validation comes from the PGEnv tool schemas; `tool_mode` and a private DBA-Bench tool list are no longer maintained;
- Expert trajectory search covers terminal candidates, DB-GPT stochastic branch selection, random vote candidates, vote value backpropagation, and value-based final selection;
- Expert root cause / solution are generated by the LLM from the tool trajectory; empty outputs raise an error immediately;
- Roundtable review uses all expert diagnosis context and passes already-generated reviews to subsequent experts and the ChiefDBA report;
- The old `dbot_tree` is explicitly rejected; native tools are supported via the existing `LLMAgent.set_tools()` / SDK `tools` parameter;
- In native mode, when the model returns no tool call and parsing falls back to text ReAct, user/assistant messages are still written into the conversation in pairs for `token_accounting` replay;
- The trajectory tree stores only compact observations, former candidates / vote use candidate summaries, the reporter prompt contains no diagnosis process, and citation marking is submitted through the two parameters of the `mark_citations` tool (with test cases for both text mode and native mode);
- The DB-GPT trajectory tree helper retains the `Thought/Action/Action Input/Observation` structure.
