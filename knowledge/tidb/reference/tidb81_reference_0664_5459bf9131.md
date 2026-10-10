# SHOW MASTER STATUS syntax, example output, and compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-show-master-status.md`
- Source Title: `SHOW MASTER STATUS`
- Source Heading Path: `SHOW MASTER STATUS | SHOW MASTER STATUS > Examples | SHOW MASTER STATUS > MySQL compatibility | SHOW MASTER STATUS > See also`
- Source Line Ranges: `5-48`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `show master status`, `tso`, `mysql compatibility`, `sql statement`, `binlog status`, `alias statement`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0664_5459bf9131`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-show-master-status.md#show-master-status`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `95ccec52721d86fd68e427bd2dade0a3b26859b710070820cc3bc002312e073f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-master-status#show-master-status
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-show-master-status.md

## Retrieval Guidance

- Use When: Use this when identifying what `SHOW MASTER STATUS` returns in TiDB, how its output maps to MySQL-style columns, or whether `SHOW BINARY LOG STATUS` is an alias.
- Retrieval Keywords: SHOW MASTER STATUS, SHOW BINARY LOG STATUS, latest TSO, tidb-binlog, Position, Binlog_Do_DB, Binlog_Ignore_DB, Executed_Gtid_Set, MySQL compatibility, binlog location information, alias statement
- Follow-up Guidance: The same source also points to `SHOW PUMP STATUS`, `SHOW DRAINER STATUS`, `CHANGE PUMP STATUS`, `CHANGE DRAINER STATUS`, and `SHOW TABLE STATUS`.
- Classification Note: This is reference content because it defines the `SHOW MASTER STATUS` statement, shows example output, and explains its MySQL compatibility and alias behavior.

## Official Source Content

# SHOW MASTER STATUS

The `SHOW MASTER STATUS` statement displays the latest TSO in the cluster.
## Examples

```sql
SHOW MASTER STATUS;
```

```sql
+-------------+--------------------+--------------+------------------+-------------------+
| File        | Position           | Binlog_Do_DB | Binlog_Ignore_DB | Executed_Gtid_Set |
+-------------+--------------------+--------------+------------------+-------------------+
| tidb-binlog | 416916363252072450 |              |                  |                   |
+-------------+--------------------+--------------+------------------+-------------------+
1 row in set (0.00 sec)
```
## MySQL compatibility

The output of `SHOW MASTER STATUS` is designed to match MySQL. However, the execution results are different in that the MySQL result is the binlog location information and the TiDB result is the latest TSO information.

The `SHOW BINARY LOG STATUS` statement was added in TiDB as an alias for `SHOW MASTER STATUS`, which has been deprecated in MySQL 8.2.0 and newer versions. 
## See also

* [SHOW PUMP STATUS](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-pump-status)
* [SHOW DRAINER STATUS](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-drainer-status)
* [CHANGE PUMP STATUS](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-change-pump)
* [CHANGE DRAINER STATUS](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-change-drainer)

* [`SHOW TABLE STATUS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-table-status)
