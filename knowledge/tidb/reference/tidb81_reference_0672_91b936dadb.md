# SHOW PUMP STATUS syntax, example output, compatibility, and related statements

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-show-pump-status.md`
- Source Title: `SHOW PUMP STATUS`
- Source Heading Path: `SHOW PUMP STATUS | SHOW PUMP STATUS > Examples | SHOW PUMP STATUS > MySQL compatibility | SHOW PUMP STATUS > See also`
- Source Line Ranges: `5-41`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: none
- Topic Tags: `show statement`, `pump`, `status`, `mysql compatibility`, `sql extension`, `binlog`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0672_91b936dadb`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-show-pump-status.md#show-pump-status`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7bb59358d29d4f0c6e5316d109de67948ca25c1a2a00666e9e9cb76d5a14ae17`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-pump-status#show-pump-status
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-show-pump-status.md

## Retrieval Guidance

- Use When: Use this chunk when you need the syntax, example output columns, or compatibility note for checking the status information of all Pump nodes with `SHOW PUMP STATUS`.
- Retrieval Keywords: SHOW PUMP STATUS, Pump nodes, binlog, NodeID, Address, State, Max_Commit_Ts, Update_Time, TiDB extension to MySQL syntax, SHOW DRAINER STATUS, CHANGE PUMP STATUS, CHANGE DRAINER STATUS, self-managed, not available on TiDB Cloud
- Follow-up Guidance: The source also points to the related statements `SHOW DRAINER STATUS`, `CHANGE PUMP STATUS`, and `CHANGE DRAINER STATUS`.
- Classification Note: This is a SQL reference chunk for a show statement that returns Pump node status information, including example result fields and a MySQL compatibility note.

## Official Source Content

# SHOW PUMP STATUS

The `SHOW PUMP STATUS` statement displays the status information for all Pump nodes in the cluster.

> **Note:**
>
> This feature is only applicable to TiDB Self-Managed and not available on [TiDB Cloud](https://docs.pingcap.com/tidbcloud/).
## Examples

```sql
SHOW PUMP STATUS;
```

```sql
+--------|----------------|--------|--------------------|---------------------|
| NodeID |     Address    | State  |   Max_Commit_Ts    |    Update_Time      |
+--------|----------------|--------|--------------------|---------------------|
| pump1  | 127.0.0.1:8250 | Online | 408553768673342237 | 2019-05-01 00:00:01 |
+--------|----------------|--------|--------------------|---------------------|
| pump2  | 127.0.0.2:8250 | Online | 408553768673342335 | 2019-05-01 00:00:02 |
+--------|----------------|--------|--------------------|---------------------|
2 rows in set (0.00 sec)
```
## MySQL compatibility

This statement is a TiDB extension to MySQL syntax.
## See also

* [SHOW DRAINER STATUS](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-drainer-status)
* [CHANGE PUMP STATUS](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-change-pump)
* [CHANGE DRAINER STATUS](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-change-drainer)
