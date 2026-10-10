# CHANGE DRAINER statement usage and examples

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-change-drainer.md`
- Source Title: `CHANGE DRAINER`
- Source Heading Path: `CHANGE DRAINER | CHANGE DRAINER > Examples | CHANGE DRAINER > MySQL compatibility | CHANGE DRAINER > See also`
- Source Line Ranges: `5-74`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `pd`
- Topic Tags: `change drainer`, `drainer`, `node state`, `pd state`, `mysql compatibility`, `examples`, `show drainer status`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0545_68c653c2e7`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-change-drainer.md#change-drainer`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `817ac202393bb98815724cf493bb9bbe911633d1821dde209f9e40881ee5049f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-change-drainer#change-drainer
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-change-drainer.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB SQL statement that modifies Drainer status information in PD, especially after checking SHOW DRAINER STATUS and seeing a Drainer state inconsistent with its actual abnormal condition.
- Retrieval Keywords: CHANGE DRAINER, SHOW DRAINER STATUS, Drainer, PD, NODE_STATE, NODE_ID, CHANGE DRAINER TO NODE_STATE ='paused' FOR NODE_ID 'drainer1', Paused, Online, state information stored in PD, TiDB extension to MySQL syntax
- Follow-up Guidance: The source also points to SHOW DRAINER STATUS, SHOW PUMP STATUS, and CHANGE PUMP STATUS as related statements.
- Classification Note: This is reference content because it defines the CHANGE DRAINER statement, its self-managed applicability, MySQL compatibility, and a concrete SQL example for changing a Drainer node state.

## Official Source Content

# CHANGE DRAINER

The `CHANGE DRAINER` statement modifies the status information for Drainer in the cluster.

> **Note:**
>
> This feature is only applicable to TiDB Self-Managed and not available on [TiDB Cloud](https://docs.pingcap.com/tidbcloud/).

> **Tip:**
>
> Drainer's state is automatically reported to PD while running. Only when Drainer is under abnormal circumstances and its state is inconsistent with the state information stored in PD, you can use the `CHANGE DRAINER` statement to modify the state information stored in PD.
## Examples

```sql
SHOW DRAINER STATUS;
```

```sql
+----------|----------------|--------|--------------------|---------------------|
|  NodeID  |     Address    | State  |   Max_Commit_Ts    |    Update_Time      |
+----------|----------------|--------|--------------------|---------------------|
| drainer1 | 127.0.0.3:8249 | Online | 408553768673342532 | 2019-04-30 00:00:03 |
+----------|----------------|--------|--------------------|---------------------|
| drainer2 | 127.0.0.4:8249 | Online | 408553768673345531 | 2019-05-01 00:00:04 |
+----------|----------------|--------|--------------------|---------------------|
2 rows in set (0.00 sec)
```

It can be seen that drainer1's state has not been updated for more than a day, the Drainer is in an abnormal state, but the `State` remains `Online`. After using `CHANGE DRAINER`, the Drainer's `State` is changed to 'paused':

```sql
CHANGE DRAINER TO NODE_STATE ='paused' FOR NODE_ID 'drainer1';
```

```sql
Query OK, 0 rows affected (0.01 sec)
```

```sql
SHOW DRAINER STATUS;
```

```sql
+----------|----------------|--------|--------------------|---------------------|
|  NodeID  |     Address    | State  |   Max_Commit_Ts    |    Update_Time      |
+----------|----------------|--------|--------------------|---------------------|
| drainer1 | 127.0.0.3:8249 | Paused | 408553768673342532 | 2019-04-30 00:00:03 |
+----------|----------------|--------|--------------------|---------------------|
| drainer2 | 127.0.0.4:8249 | Online | 408553768673345531 | 2019-05-01 00:00:04 |
+----------|----------------|--------|--------------------|---------------------|
2 rows in set (0.00 sec)
```
## MySQL compatibility

This statement is a TiDB extension to MySQL syntax.
## See also

* [SHOW PUMP STATUS](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-pump-status)
* [SHOW DRAINER STATUS](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-drainer-status)
* [CHANGE PUMP STATUS](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-change-pump)
