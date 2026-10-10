# PLAN REPLAYER CAPTURE overview and enablement

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-plan-replayer.md`
- Source Title: `Use PLAN REPLAYER to Save and Restore the On-Site Information of a Cluster`
- Source Heading Path: `Use PLAN REPLAYER to Save and Restore the On-Site Information of a Cluster > Use `PLAN REPLAYER CAPTURE` to capture target plans | Use PLAN REPLAYER to Save and Restore the On-Site Information of a Cluster > Use `PLAN REPLAYER CAPTURE` to capture target plans > Enable `PLAN REPLAYER CAPTURE``
- Source Line Ranges: `201-216`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `shared`
- Topic Tags: `plan-replayer-capture`, `capture`, `execution-plan`, `optimizer`, `system-variable`, `target-query`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0064_929663cf6a`
- Source ID: `tidb-docs-8.1:sql-plan-replayer.md#use-plan-replayer-capture-to-capture-target-plans`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5585ef6ffef4d281529f5ed725fbed51a574954ef5004068b222bb77412ad4a0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-plan-replayer#use-plan-replayer-capture-to-capture-target-plans
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-plan-replayer.md

## Retrieval Guidance

- Use When: Use this when you need to identify PLAN REPLAYER CAPTURE behavior for occasional target SQL and plans, or the system variable that enables capture.
- Retrieval Keywords: PLAN REPLAYER CAPTURE, tidb_enable_plan_replayer_capture, capture target plans, optimizer-related information, target SQL statement, digest of the target execution plan, matching tasks, system table, historical files
- Follow-up Guidance: To enable PLAN REPLAYER CAPTURE, set the system variable tidb_enable_plan_replayer_capture to ON.
- Classification Note: This is classified as diagnosis because the content describes capturing optimizer information for intermittent target queries and execution plans to support troubleshooting.

## Official Source Content

## Use `PLAN REPLAYER CAPTURE` to capture target plans

When you locate the execution plan of TiDB in some scenarios, the target SQL statement and the target execution plan might only appear occasionally in the query, so you cannot directly capture the statement and the plan using `PLAN REPLAYER`. In such cases, you can use `PLAN REPLAYER CAPTURE` to help you capture the optimizer information of the target SQL statement and the target plan.

`PLAN REPLAYER CAPTURE` has the following main features:

- Registers the target SQL statement and the digest of the target execution plan in the TiDB cluster in advance, and starts matching the target query.
- When the target query is matched successfully, directly captures its optimizer-related information and exports it as a ZIP file.
- For each matched SQL and execution plan, the information is only captured once.
- Displays the ongoing matching tasks and generated files through the system table.
- Periodically cleans up historical files.
### Enable `PLAN REPLAYER CAPTURE`

`PLAN REPLAYER CAPTURE` is controlled by the system variable [`tidb_enable_plan_replayer_capture`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_plan_replayer_capture). To enable `PLAN REPLAYER CAPTURE`, set the value of the system variable to `ON`.
