# JDBC query timeout and support resources

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-timeouts-in-tidb.md`
- Source Title: `Timeouts in TiDB`
- Source Heading Path: `Timeouts in TiDB > JDBC query timeout | Timeouts in TiDB > Need help?`
- Source Line Ranges: `77-122`
- Source Scope: `developer`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `jdbc`, `query-timeout`, `global-kill`, `wait-timeout`, `interactive-timeout`, `max-execution-time`, `java-applications`, `connection-timeout`, `support`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0020_68757fa861`
- Source ID: `tidb-docs-8.1:develop/dev-guide-timeouts-in-tidb.md#jdbc-query-timeout`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ae1d30bc9e37cfbb6b48a35d0a70f8916c11b55c0de9169de5ba44d9816501c4`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-timeouts-in-tidb#jdbc-query-timeout
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-timeouts-in-tidb.md

## Retrieval Guidance

- Use When: Use this chunk when investigating JDBC query timeout behavior, MySQL-compatible connection timeout variables, or where to get help for TiDB timeout issues.
- Retrieval Keywords: JDBC query timeout, setQueryTimeout(), enable-global-kill, global kill, KILL command, max_execution_time, wait_timeout, interactive_timeout, sessionVariables=wait_timeout=3600, sessionVariables=max_execution_time=300000, MySQL-compatible timeout control parameters, Discord, Slack, submit a support ticket
- Follow-up Guidance: The source lists community help channels on Discord and Slack and a support ticket submission link.
- Classification Note: This chunk is classified as diagnosis because it describes when JDBC query timeout works in TiDB, which timeout parameters affect connections and SQL execution, and where to seek support.

## Official Source Content

## JDBC query timeout

Starting from v6.1.0, when the [`enable-global-kill`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#enable-global-kill-new-in-v610) configuration item is set to its default value `true`, you can use the `setQueryTimeout()` method provided by MySQL JDBC to control the query timeout.

> **Note:**
>
> When your TiDB version is earlier than v6.1.0 or [`enable-global-kill`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#enable-global-kill-new-in-v610) is set to `false`, `setQueryTimeout()` does not work for TiDB. This is because the client sends a `KILL` command to the database when it detects the query timeout. However, because the TiDB service is load balanced, TiDB does not execute the `KILL` command to avoid termination of the connection on a wrong TiDB node. In such cases, you can use `max_execution_time` to control query timeout.

Starting from v6.1.0, when the [`enable-global-kill`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file/#enable-global-kill-new-in-v610) configuration item is set to its default value `true`, you can use the `setQueryTimeout()` method provided by MySQL JDBC to control the query timeout.

> **Note:**
>
> When your TiDB version is earlier than v6.1.0 or [`enable-global-kill`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file/#enable-global-kill-new-in-v610) is set to `false`, `setQueryTimeout()` does not work for TiDB. This is because the client sends a `KILL` command to the database when it detects the query timeout. However, because the TiDB service is load balanced, TiDB does not execute the `KILL` command to avoid termination of the connection on a wrong TiDB node. In such cases, you can use `max_execution_time` to control query timeout.

TiDB provides the following MySQL-compatible timeout control parameters.

- **wait_timeout**, controls the non-interactive idle timeout for the connection to Java applications. Since TiDB v5.4, the default value of `wait_timeout` is `28800` seconds, which is 8 hours. For TiDB versions earlier than v5.4, the default value is `0`, which means the timeout is unlimited.
- **interactive_timeout**, controls the interactive idle timeout for the connection to Java applications. The value is `8 hours` by default.
- **max_execution_time**, controls the timeout for SQL execution in the connection, only effective for read-only SQL statements. The value is `0` by default, which allows the connection to be infinitely busy, that is, an SQL statement is executed for an infinitely long time.

However, in a real production environment, idle connections and indefinitely executing SQL statements have a negative effect on both the database and the application. You can avoid idle connections and indefinitely executing SQL statements by configuring these two session-level variables in your application's connection string. For example, set the following:

- `sessionVariables=wait_timeout=3600` (1 hour)
- `sessionVariables=max_execution_time=300000` (5 minutes)
## Need help?

Ask the community on [Discord](https://discord.gg/DQZ2dy3cuc?utm_source=doc) or [Slack](https://slack.tidb.io/invite?team=tidb-community&channel=everyone&ref=pingcap-docs), or [submit a support ticket](https://docs.pingcap.com/tidb/stable/support).

Ask the community on [Discord](https://discord.gg/DQZ2dy3cuc?utm_source=doc) or [Slack](https://slack.tidb.io/invite?team=tidb-community&channel=everyone&ref=pingcap-docs), or [submit a support ticket](https://tidb.support.pingcap.com/).
