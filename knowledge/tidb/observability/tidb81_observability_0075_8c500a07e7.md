# Observability features in v6.6.0

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.6.0.md`
- Source Title: `TiDB 6.6.0 Release Notes`
- Source Heading Path: `TiDB 6.6.0 Release Notes > Feature details > Observability`
- Source Line Ranges: `255-312`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `dashboard`, `tidb`
- Topic Tags: `sql-binding`, `plan-cache`, `slow-query-log`, `plan-replayer`, `statement-summary`, `diagnostics`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0075_8c500a07e7`
- Source ID: `tidb-docs-8.1:releases/release-6.6.0.md#observability`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `279aad5111906cf5b3eb93c86ca63b68462f2f61084b29e49cc4246b842a51e7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.6.0#observability
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.6.0.md

## Retrieval Guidance

- Use When: Use this chunk when searching TiDB v6.6.0 observability changes around SQL binding in TiDB Dashboard, plan cache diagnostics warnings, slow query log warnings, PLAN REPLAYER CAPTURE, or persisted statements summary.
- Retrieval Keywords: TiDB 6.6.0 Observability, TiDB Dashboard fast plan binding, creating SQL binding from statement history, Add warning for caching execution plans, SHOW WARNINGS, skip plan-cache: '1' may be converted to INT, sql-prepared-plan-cache diagnostics, Warnings field slow query log, slow query page of TiDB Dashboard, PLAN REPLAYER CAPTURE, tidb_enable_plan_replayer_capture, automatically capture the generation of SQL execution plans, statement summary persistence, persisting statements summary, statement-summary-tables
- Follow-up Guidance: The source points to related documentation for fast plan binding, prepared plan cache diagnostics, identifying slow queries, PLAN REPLAYER capture, and persisting statements summary.
- Classification Note: This is classified as observability because the content describes diagnosis and visibility features for SQL plans, warnings, slow queries, PLAN REPLAYER capture, and statements summary history.

## Official Source Content

### Observability

* Support quickly creating SQL binding on TiDB Dashboard [#781](https://github.com/pingcap/tidb-dashboard/issues/781) @[YiniXu9506](https://github.com/YiniXu9506)

    TiDB v6.6.0 supports creating SQL binding from statement history, which allows you to quickly bind a SQL statement to a specific plan on TiDB Dashboard.

    By providing a user-friendly interface, this feature simplifies the process of binding plans in TiDB, reduces the operation complexity, and improves the efficiency and user experience of the plan binding process.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-statement-details#fast-plan-binding).

* Add warning for caching execution plans @[qw4990](https://github.com/qw4990)

    When an execution plan cannot be cached, TiDB indicates the reason in warning to make diagnostics easier. For example:

    ```sql
    mysql> PREPARE st FROM 'SELECT * FROM t WHERE a<?';
    Query OK, 0 rows affected (0.00 sec)

    mysql> SET @a='1';
    Query OK, 0 rows affected (0.00 sec)

    mysql> EXECUTE st USING @a;
    Empty set, 1 warning (0.01 sec)

    mysql> SHOW WARNINGS;
    +---------+------+----------------------------------------------+
    | Level   | Code | Message                                      |
    +---------+------+----------------------------------------------+
    | Warning | 1105 | skip plan-cache: '1' may be converted to INT |
    +---------+------+----------------------------------------------+
    ```

    In the preceding example, the optimizer converts a non-INT type to an INT type, and the execution plan might change with the change of the parameter, so TiDB does not cache the plan.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/sql-prepared-plan-cache#diagnostics-of-prepared-plan-cache).

* Add a `Warnings` field to the slow query log [#39893](https://github.com/pingcap/tidb/issues/39893) @[time-and-fate](https://github.com/time-and-fate)

    TiDB v6.6.0 adds a `Warnings` field to the slow query log to help diagnose performance issues. This field records warnings generated during the execution of a slow query. You can also view the warnings on the slow query page of TiDB Dashboard.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/identify-slow-queries).

* Automatically capture the generation of SQL execution plans [#38779](https://github.com/pingcap/tidb/issues/38779) @[Yisaer](https://github.com/Yisaer)

    In the process of troubleshooting execution plan issues, `PLAN REPLAYER` can help preserve the scene and improve the efficiency of diagnosis. However, in some scenarios, the generation of some execution plans cannot be reproduced freely, which makes the diagnosis work more difficult.

    To address such issues, in TiDB v6.6.0, `PLAN REPLAYER` extends the capability of automatic capture. With the `PLAN REPLAYER CAPTURE` command, you can register the target SQL statement in advance and also specify the target execution plan at the same time. When TiDB detects the SQL statement or the execution plan that matches the registered target, it automatically generates and packages the `PLAN REPLAYER` information. When the execution plan is unstable, this feature can improve diagnostic efficiency.

    To use this feature, set the value of [`tidb_enable_plan_replayer_capture`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_plan_replayer_capture) to `ON`.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/sql-plan-replayer#use-plan-replayer-capture).

* Support persisting statements summary (experimental) [#40812](https://github.com/pingcap/tidb/issues/40812) @[mornyx](https://github.com/mornyx)

    Before v6.6.0, statements summary data is kept in memory and would be lost upon a TiDB server restart. Starting from v6.6.0, TiDB supports enabling statements summary persistence, which allows historical data to be written to disks on a regular basis. In the meantime, the result of queries on system tables will derive from disks, instead of memory. After TiDB restarts, all historical data remains available.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/statement-summary-tables#persist-statements-summary).
