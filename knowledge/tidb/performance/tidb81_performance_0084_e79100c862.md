# Execution plan control methods overview

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/control-execution-plan.md`
- Source Title: `Control Execution Plan`
- Source Heading Path: `Control Execution Plan`
- Source Line Ranges: `5-24`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `execution-plan`, `optimizer-hints`, `sql-plan-management`, `blocklist`, `system-variables`, `optimizer-fix-control`, `upgrade-regression`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0084_e79100c862`
- Source ID: `tidb-docs-8.1:control-execution-plan.md#control-execution-plan`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `022c5e37a70906ff1a9c868c5d80fed699411abf4cf1c5a15f2203f5b9252c33`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/control-execution-plan#control-execution-plan
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/control-execution-plan.md

## Retrieval Guidance

- Use When: Use this chunk when asking for the available TiDB methods to control execution plan generation or to address plan instability and optimizer behavior changes after upgrades.
- Retrieval Keywords: Control Execution Plan, Optimizer Hints, SQL Plan Management, Blocklist of Optimization Rules and Expression Pushdown, blocklist, system variables, session level, system level, tidb_opt_fix_control, Optimizer Fix Controls, execution plan instability, version upgrades, cluster performance degradation, performance regression, optimizer behavior changes
- Follow-up Guidance: The source points to Optimizer Hints, SQL Plan Management, Blocklist of Optimization Rules and Expression Pushdown, and Optimizer Fix Controls for more detailed introductions.
- Classification Note: Classified as performance for the TiDB SQL optimizer because the content is an overview of mechanisms that control execution plan generation, including hints, SQL plan management, blocklist, and optimizer-related system variables.

## Official Source Content

# Control Execution Plan

The first two chapters of SQL Tuning introduce how to understand TiDB's execution plan and how TiDB generates an execution plan. This chapter introduces what methods can be used to control the generation of the execution plan when you determine the problems with the execution plan. This chapter mainly includes the following three aspects:

- In [Optimizer Hints](https://docs.pingcap.com/tidb/stable/optimizer-hints), you will learn how to use hints to guide TiDB to generate an execution plan.
- But hints change the SQL statement intrusively. In some scenarios, hints cannot be simply inserted. In [SQL Plan Management](https://docs.pingcap.com/tidb/stable/sql-plan-management), you will know how TiDB uses another syntax to non-intrusively control the generation of execution plans, and the methods of automatic execution plan evolution in the background. This method helps address issues such as execution plan instability caused by version upgrades and cluster performance degradation.
- Finally, you will learn how to use the blocklist in [Blocklist of Optimization Rules and Expression Pushdown](https://docs.pingcap.com/tidb/stable/blocklist-control-plan).

Besides the preceding methods, the execution plan is also affected by some system variables. By modifying these variables at the system level or session level, you can control the generation of the execution plan. Starting from v6.5.3 and v7.1.0, TiDB introduces a relatively special variable [`tidb_opt_fix_control`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_fix_control-new-in-v653-and-v710). This variable can accept multiple control items to control the behavior of the optimizer in a more fine-grained way, to prevent performance regression caused by behavior changes in the optimizer after cluster upgrade. Refer to [Optimizer Fix Controls](https://docs.pingcap.com/tidb/stable/optimizer-fix-controls) for a more detailed introduction.

Besides the preceding methods, the execution plan is also affected by some system variables. By modifying these variables at the system level or session level, you can control the generation of the execution plan. Starting from v6.5.3 and v7.1.0, TiDB introduces a relatively special variable [`tidb_opt_fix_control`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_fix_control-new-in-v653-and-v710). This variable can accept multiple control items to control the behavior of the optimizer in a more fine-grained way, to prevent performance regression caused by behavior changes in the optimizer after cluster upgrade. Refer to [Optimizer Fix Controls](https://docs.pingcap.com/tidb/v7.2/optimizer-fix-controls) for a more detailed introduction.
