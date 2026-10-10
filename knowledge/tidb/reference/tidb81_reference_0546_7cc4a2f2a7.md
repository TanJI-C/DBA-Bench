# CHANGE PUMP statement usage and examples

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-change-pump.md`
- Source Title: `CHANGE PUMP`
- Source Heading Path: `CHANGE PUMP | CHANGE PUMP > Examples | CHANGE PUMP > MySQL compatibility | CHANGE PUMP > See also`
- Source Line Ranges: `5-74`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `pd`
- Topic Tags: `change-pump`, `pump`, `node-state`, `sql-syntax`, `mysql-compatibility`, `status-management`, `examples`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0546_7cc4a2f2a7`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-change-pump.md#change-pump`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e87151309bd1f4874f6288c83b75d82c442a54cf3e07d8238fb52ec3c441c266`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-change-pump#change-pump
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-change-pump.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the SQL syntax and example for modifying Pump state information stored in PD with the CHANGE PUMP statement after SHOW PUMP STATUS shows an abnormal or stale Pump state.
- Retrieval Keywords: CHANGE PUMP, SHOW PUMP STATUS, CHANGE PUMP TO NODE_STATE ='paused' FOR NODE_ID 'pump1', NODE_STATE, NODE_ID, Pump, PD, Paused, Online, TiDB extension to MySQL syntax, CHANGE DRAINER STATUS, SHOW DRAINER STATUS
- Follow-up Guidance: The source also points to SHOW PUMP STATUS, SHOW DRAINER STATUS, and CHANGE DRAINER STATUS as related statements.
- Classification Note: This is reference content because it defines the CHANGE PUMP statement, states its applicability to TiDB Self-Managed, and provides exact SQL examples and MySQL compatibility information.

## Official Source Content

# CHANGE PUMP

The `CHANGE PUMP` statement modifies the status information for Pump in the cluster.

> **Note:**
>
> This feature is only applicable to TiDB Self-Managed and not available on [TiDB Cloud](https://docs.pingcap.com/tidbcloud/).

> **Tip:**
>
> Pump's state is automatically reported to PD while running. Only when Pump is under abnormal circumstances and its state is inconsistent with the state information stored in PD, you can use the `CHANGE PUMP` statement to modify the state information stored in PD.
## Examples

```sql
SHOW PUMP STATUS;
```

```sql
+--------|----------------|--------|--------------------|---------------------|
| NodeID |     Address    | State  |   Max_Commit_Ts    |    Update_Time      |
+--------|----------------|--------|--------------------|---------------------|
| pump1  | 127.0.0.1:8250 | Online | 408553768673342237 | 2019-04-30 00:00:01 |
+--------|----------------|--------|--------------------|---------------------|
| pump2  | 127.0.0.2:8250 | Online | 408553768673342335 | 2019-05-01 00:00:02 |
+--------|----------------|--------|--------------------|---------------------|
2 rows in set (0.00 sec)
```

It can be seen that pump1's state has not been updated for more than a day, the Pump is in an abnormal state, but the `State` remains `Online`. After using `CHANGE PUMP`, the Pump's `State` is changed to 'paused' :

```sql
CHANGE PUMP TO NODE_STATE ='paused' FOR NODE_ID 'pump1';
```

```sql
Query OK, 0 rows affected (0.01 sec)
```

```sql
SHOW PUMP STATUS;
```

```sql
+--------|----------------|--------|--------------------|---------------------|
| NodeID |     Address    | State  |   Max_Commit_Ts    |    Update_Time      |
+--------|----------------|--------|--------------------|---------------------|
| pump1  | 127.0.0.1:8250 | Paused | 408553768673342237 | 2019-04-30 00:00:01 |
+--------|----------------|--------|--------------------|---------------------|
| pump2  | 127.0.0.2:8250 | Online | 408553768673342335 | 2019-05-01 00:00:02 |
+--------|----------------|--------|--------------------|---------------------|
2 rows in set (0.00 sec)
```
## MySQL compatibility

This statement is a TiDB extension to MySQL syntax.
## See also

* [SHOW PUMP STATUS](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-pump-status)
* [SHOW DRAINER STATUS](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-drainer-status)
* [CHANGE DRAINER STATUS](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-change-drainer)
