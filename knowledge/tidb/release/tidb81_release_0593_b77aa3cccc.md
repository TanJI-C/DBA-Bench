# Feature details: SQL, DXF, log desensitization, and data migration updates

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-8.1.0.md`
- Source Title: `TiDB 8.1.0 Release Notes`
- Source Heading Path: `TiDB 8.1.0 Release Notes > Feature details > SQL | TiDB 8.1.0 Release Notes > Feature details > DB operations | TiDB 8.1.0 Release Notes > Feature details > Security | TiDB 8.1.0 Release Notes > Feature details > Data migration`
- Source Line Ranges: `108-159`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `lightning`, `ticdc`
- Topic Tags: `ga`, `sql`, `default-values`, `add-column`, `distributed-execution-framework`, `add-index`, `import-into`, `log-redaction`, `security`, `data-migration`, `conflict-resolution`, `mtls`, `client-authentication`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0593_b77aa3cccc`
- Source ID: `tidb-docs-8.1:releases/release-8.1.0.md#sql`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ee84c9f631721ae47de644a71fba7565e60b6157733481af8ad1220cc64a4b3d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-8.1.0#sql
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-8.1.0.md

## Retrieval Guidance

- Use When: Use this chunk when searching for TiDB 8.1.0 release notes about GA SQL defaults, DXF task execution, log redaction, IMPORT INTO, Lightning conflict handling, or TiCDC client authentication.
- Retrieval Keywords: GA default column values expressions, ADD COLUMN expressions as default values, DATE_FORMAT default value, TiDB Distributed eXecution Framework, tidb_enable_dist_task, ADD INDEX, IMPORT INTO, tidb_redact_log, collect-log subcommand, IMPORT INTO ... FROM SELECT, conflict.strategy, replace strategy, TiDB Lightning logical import mode, physical import mode, TiCDC client authentication, client certificates, mutual Transport Layer Security (mTLS), TiDB username and password
- Follow-up Guidance: See the linked documentation pages for the detailed syntax and configuration references.
- Classification Note: This chunk is classified as release feature details covering SQL, DB operations, security, and data migration changes in TiDB 8.1.0.

## Official Source Content

### SQL

* Support using more expressions to set default column values when creating a table (GA) [#50936](https://github.com/pingcap/tidb/issues/50936) @[zimulala](https://github.com/zimulala)

    Before v8.0.0, when you create a table, the default value of a column is limited to strings, numbers, dates, and certain expressions. Starting from v8.0.0, you can use more expressions as the default column values. For example, you can set the default value of a column to `DATE_FORMAT`. This feature helps you meet more diverse requirements. In v8.1.0, this feature becomes GA.

    Starting from v8.1.0, you can use expressions as default values when adding columns by `ADD COLUMN`.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/data-type-default-values#specify-expressions-as-default-values).
### DB operations

* Enable the TiDB Distributed eXecution Framework (DXF) by default to enhance the performance and stability of `ADD INDEX` or `IMPORT INTO` tasks in parallel execution [#52441](https://github.com/pingcap/tidb/issues/52441) @[D3Hunter](https://github.com/D3Hunter)

    The DXF becomes generally available (GA) in v7.5.0, but it is disabled by default. This means that an `ADD INDEX` or `IMPORT INTO` task is executed only by one TiDB node by default.

    Starting from v8.1.0, TiDB enables this feature by default ([`tidb_enable_dist_task`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_dist_task-new-in-v710) defaults to `ON`). When enabled, the DXF can schedule multiple TiDB nodes to execute the same `ADD INDEX` or `IMPORT INTO` task in parallel, fully utilizing the resources of the TiDB cluster and greatly improving the performance of these tasks. In addition, you can linearly improve the performance of `ADD INDEX` and `IMPORT INTO` tasks by adding TiDB nodes and configuring [`tidb_service_scope`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_service_scope-new-in-v740) for the newly added nodes.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/tidb-distributed-execution-framework).
### Security

* Enhance TiDB log desensitization (GA) [#52364](https://github.com/pingcap/tidb/issues/52364) @[xhebox](https://github.com/xhebox)

    The enhanced TiDB log desensitization supports removing sensitive data when users view logs, implemented by marking SQL text information in log files. You can control whether to mark log information to enable secure use of TiDB logs in different scenarios, enhancing the security and flexibility of using log desensitization. To use this feature, set the system variable `tidb_redact_log` to `MARKER`, and then the SQL text in TiDB's runtime logs is marked. In addition, you can use the `collect-log` subcommand on the TiDB server to remove marked sensitive data from the logs and display the logs in a secure manner. You can also remove all markers and get the normal logs. This feature became generally available in v8.1.0.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/system-variables#tidb_redact_log).
### Data migration

* Support the `IMPORT INTO ... FROM SELECT` syntax (GA) [#49883](https://github.com/pingcap/tidb/issues/49883) @[D3Hunter](https://github.com/D3Hunter)

    Before v8.0.0, importing query results into a target table could only be done using the `INSERT INTO ... SELECT` statement, which is relatively inefficient in some large dataset scenarios. In v8.0.0, TiDB introduces `IMPORT INTO ... FROM SELECT` as an experimental feature, which enables you to import the results of a `SELECT` query into an empty TiDB target table. It achieves up to 8 times the performance of `INSERT INTO ... SELECT` and significantly reduces the import time. In addition, you can use `IMPORT INTO ... FROM SELECT` to import historical data queried with [`AS OF TIMESTAMP`](https://docs.pingcap.com/tidb/stable/as-of-timestamp).

    In v8.1.0, the `IMPORT INTO ... FROM SELECT` syntax becomes generally available (GA), enriching the functionality scenarios of the `IMPORT INTO` statement.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-import-into).

* TiDB Lightning simplifies conflict resolution strategies and supports handling conflicting data using the `replace` strategy (GA) [#51036](https://github.com/pingcap/tidb/issues/51036) @[lyzx2001](https://github.com/lyzx2001)

    Before v8.0.0, TiDB Lightning has [one data conflict resolution strategy](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-logical-import-mode-usage#conflict-detection) for the logical import mode and [two data conflict resolution strategies](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-physical-import-mode-usage#conflict-detection) for the physical import mode, which are not easy to understand and configure.

    In v8.0.0, TiDB Lightning deprecates the [old version of conflict detection](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-physical-import-mode-usage#the-old-version-of-conflict-detection-deprecated-in-v800) strategy for the physical import mode, enables you to control the conflict detection strategy for both logical and physical import modes via the [`conflict.strategy`](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration) parameter (experimental), and simplifies the configuration of this parameter. In addition, in the physical import mode, the `replace` strategy supports retaining the latest data and overwriting the old data when the import detects data with primary key or unique key conflicts. In v8.1.0, the capability to handle conflicting data with the `replace` strategy becomes generally available (GA).

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration).

* TiCDC supports client authentication [#10636](https://github.com/pingcap/tiflow/issues/10636) @[CharlesCheung96](https://github.com/CharlesCheung96)

    In v8.1.0, TiCDC supports client authentication when you are using the TiCDC CLI or OpenAPI. This feature enables you to configure TiCDC to require client authentication using client certificates, thereby establishing mutual Transport Layer Security (mTLS). Additionally, you can configure authentication based on TiDB username and password.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-client-authentication).
