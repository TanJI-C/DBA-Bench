# SHOW DRAINER STATUS syntax, example output, and related statements

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-show-drainer-status.md`
- Source Title: `SHOW DRAINER STATUS`
- Source Heading Path: `SHOW DRAINER STATUS | SHOW DRAINER STATUS > Examples | SHOW DRAINER STATUS > MySQL compatibility | SHOW DRAINER STATUS > See also`
- Source Line Ranges: `5-41`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `ecosystem`
- Topic Tags: `show statement`, `drainer`, `status`, `mysql compatibility`, `examples`, `binlog`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0657_8fef92da10`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-show-drainer-status.md#show-drainer-status`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1e274d4d3012106e28d68b2e5b1582235b00324f0909d27d2254a58d48568aef`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-drainer-status#show-drainer-status
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-show-drainer-status.md

## Retrieval Guidance

- Use When: Use this when looking for the SQL statement that displays status information for all Drainer nodes in the cluster, including syntax, example output columns, MySQL compatibility, and related status statements.
- Retrieval Keywords: SHOW DRAINER STATUS, Drainer nodes, status information, NodeID, Address, State, Max_Commit_Ts, Update_Time, TiDB extension to MySQL syntax, SHOW PUMP STATUS, CHANGE PUMP STATUS, CHANGE DRAINER STATUS, binlog
- Follow-up Guidance: The page also points to SHOW PUMP STATUS, CHANGE PUMP STATUS, and CHANGE DRAINER STATUS as related statements.
- Classification Note: This is reference content because it defines the SHOW DRAINER STATUS statement, shows its example output, and notes that it is a TiDB extension to MySQL syntax and only applicable to TiDB Self-Managed.

## Official Source Content

# SHOW DRAINER STATUS

The `SHOW DRAINER STATUS` statement displays the status information for all Drainer nodes in the cluster.

> **Note:**
>
> This feature is only applicable to TiDB Self-Managed and not available on [TiDB Cloud](https://docs.pingcap.com/tidbcloud/).
## Examples

```sql
SHOW DRAINER STATUS;
```

```sql
+----------|----------------|--------|--------------------|---------------------|
|  NodeID  |     Address    | State  |   Max_Commit_Ts    |    Update_Time      |
+----------|----------------|--------|--------------------|---------------------|
| drainer1 | 127.0.0.3:8249 | Online | 408553768673342532 | 2019-05-01 00:00:03 |
+----------|----------------|--------|--------------------|---------------------|
| drainer2 | 127.0.0.4:8249 | Online | 408553768673345531 | 2019-05-01 00:00:04 |
+----------|----------------|--------|--------------------|---------------------|
2 rows in set (0.00 sec)
```
## MySQL compatibility

This statement is a TiDB extension to MySQL syntax.
## See also

* [SHOW PUMP STATUS](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-pump-status)
* [CHANGE PUMP STATUS](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-change-pump)
* [CHANGE DRAINER STATUS](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-change-drainer)
