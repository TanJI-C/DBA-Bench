# Account control and TiCDC or TiDB Binlog SQL statements overview

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-overview.md`
- Source Title: `SQL Statement Overview`
- Source Heading Path: `SQL Statement Overview > Account management / Data Control Language | SQL Statement Overview > TiCDC & TiDB Binlog`
- Source Line Ranges: `270-318`
- Source Scope: `shared`
- Primary Component: `sql`
- Related Components: `tidb`, `ticdc`, `cloud`
- Topic Tags: `account-management`, `dcl`, `users`, `roles`, `privileges`, `replication`, `binlog`, `changefeed`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0618_4f07e2176b`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-overview.md#account-management-data-control-language`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `40a3119223eaa91def2facfb5fd30e5c05a3aa7db431ff792ecf3a9d53dc0fba`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-overview#account-management-data-control-language
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-overview.md

## Retrieval Guidance

- Use When: Use this chunk when you need a reference list of account management or data control language statements, or SQL statements related to TiCDC and TiDB Binlog.
- Retrieval Keywords: ALTER USER, CREATE ROLE, CREATE USER, DROP ROLE, DROP USER, FLUSH PRIVILEGES, GRANT <privileges>, GRANT <role>, RENAME USER, REVOKE <privileges>, REVOKE <role>, SET DEFAULT ROLE, SET PASSWORD, SET ROLE, SHOW CREATE USER, SHOW GRANTS, SHOW PRIVILEGES, ADMIN [SET|SHOW|UNSET] BDR ROLE, CHANGE DRAINER, CHANGE PUMP, SHOW DRAINER STATUS, SHOW MASTER STATUS, SHOW PUMP STATUS, Account management / Data Control Language, TiCDC & TiDB Binlog, Changefeed, TiDB Cloud console
- Follow-up Guidance: The note says TiCDC and TiDB Binlog are for replicating TiDB data to the upstream for TiDB Self-Managed, that most related SQL statements are not applicable to TiDB Cloud, and that TiDB Cloud provides the Changefeed feature in the TiDB Cloud console instead.
- Classification Note: This is a reference overview because it enumerates account-management and replication-related SQL statements and gives their official short descriptions plus an applicability note.

## Official Source Content

## Account management / Data Control Language

| SQL Statement | Description |
|---------------|-------------|
| [`ALTER USER`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-user) | Modifies a user. |
| [`CREATE ROLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-role) | Creates a role. |
| [`CREATE USER`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-user) | Creates a new user. |
| [`DROP ROLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-role) | Drops an existing role. |
| [`DROP USER`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-user) | Drops an existing user. |
| [`FLUSH PRIVILEGES`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-flush-privileges) | Reloads the in-memory copy of privileges from the privilege tables. |
| [`GRANT <privileges>`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-grant-privileges) | Grants privileges. |
| [`GRANT <role>`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-grant-role) | Grants a role. |
| [`RENAME USER`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-rename-user) | Renames an existing user. |
| [`REVOKE <privileges>`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-revoke-privileges) | Revokes privileges. |
| [`REVOKE <role>`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-revoke-role) | Revokes a role. |
| [`SET DEFAULT ROLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-set-default-role) | Sets a default role. |
| [`SET PASSWORD`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-set-password) | Changes a password. |
| [`SET ROLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-set-role) | Enables roles in the current session. |
| [`SHOW CREATE USER`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-create-user) | Shows the `CREATE` statement for a user. |
| [`SHOW GRANTS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-grants) | Shows privileges associated with a user. |
| [`SHOW PRIVILEGES`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-privileges) | Shows available privileges. |
## TiCDC & TiDB Binlog

| SQL Statement | Description |
|---------------|-------------|
| [`ADMIN [SET\|SHOW\|UNSET] BDR ROLE`](/sql-statements/sql-statement-admin-bdr-role.md) | Manages BDR roles. |
| [`CHANGE DRAINER`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-change-drainer) | Modifies the status information for Drainer in the cluster. |
| [`CHANGE PUMP`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-change-pump) | Modifies the status information for Pump in the cluster. |
| [`SHOW DRAINER STATUS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-drainer-status) | Shows the status for all Drainer nodes in the cluster. |
| [`SHOW MASTER STATUS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-master-status) | Shows the latest TSO in the cluster. |
| [`SHOW PUMP STATUS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-pump-status) | Shows the status information for all Pump nodes in the cluster. |

> **Note:**
>
> [TiCDC](https://docs.pingcap.com/tidb/stable/ticdc-overview) & [TiDB Binlog](https://docs.pingcap.com/tidb/stable/tidb-binlog-overview) are tools for replicating TiDB data to the upstream for TiDB Self-Managed. Most SQL statements for TiCDC and TiDB Binlog are not applicable to TiDB Cloud. For TiDB Cloud, you can use the [Changefeed](https://docs.pingcap.com/tidb/stable/tidb-cloud/changefeed-overview) feature in the [TiDB Cloud console](https://tidbcloud.com) instead to stream data. 

| SQL Statement | Description |
|---------------|-------------|
| [`SHOW MASTER STATUS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-master-status) | Shows the latest TSO in the cluster. |
