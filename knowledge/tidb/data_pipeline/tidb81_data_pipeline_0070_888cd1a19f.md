# TiCDC rename-table and cross-database DDL considerations

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-ddl.md`
- Source Title: `Changefeed DDL Replication`
- Source Heading Path: `Changefeed DDL Replication > DDL replication considerations > DDL replication considerations for renaming tables | Changefeed DDL Replication > DDL replication considerations > DDL replication considerations for renaming tables > Rename a single table in a DDL statement | Changefeed DDL Replication > DDL replication considerations > DDL replication considerations for renaming tables > Rename multiple tables in a DDL statement | Changefeed DDL Replication > DDL replication considerations > DDL statement considerations`
- Source Line Ranges: `60-110`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `sql`
- Topic Tags: `rename table`, `filter rules`, `cross-database ddl`, `error handling`, `table renaming`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0070_888cd1a19f`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-ddl.md#ddl-replication-considerations-for-renaming-tables`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `88d820a3406970fa331d384da794b90d87586123419e64e48aaaa13c763805f3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-ddl#ddl-replication-considerations-for-renaming-tables
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-ddl.md

## Retrieval Guidance

- Use When: Use this chunk when checking how TiCDC handles `RENAME TABLE` with filter rules, multiple-table renames, swapped table names, or cross-database DDL statements.
- Retrieval Keywords: DDL replication considerations for renaming tables, RENAME TABLE, rename a single table in a DDL statement, rename multiple tables in a DDL statement, filter rules, old table name matches the filter rule, report an error and exit the replication, new database name does not match the filter rule, TiCDC does not support the `RENAME TABLE` DDL that swaps the table names, cross-database DDL statements, CREATE TABLE db1.t1 LIKE t2, CREATE TABLE db1.t1 LIKE db2.t2
- Follow-up Guidance: For cross-database DDL statements, the source says to explicitly specify all relevant database names in the DDL statement because otherwise the downstream might not execute it correctly due to missing database name information.
- Classification Note: This is classified under data_pipeline because it describes TiCDC replication constraints and error cases for DDL handling during changefeed processing.

## Official Source Content

### DDL replication considerations for renaming tables

Due to the lack of some context during the replication process, TiCDC has some constraints on the replication of `RENAME TABLE` DDLs.
#### Rename a single table in a DDL statement

If a DDL statement renames a single table, TiCDC only replicates the DDL statement when the old table name matches the filter rule. The following is an example.

Assume that the configuration file of your changefeed is as follows:

```toml
[filter]
rules = ['test.t*']
```

TiCDC processes this type of DDL as follows:

| DDL | Whether to replicate | Reason for the handling |
| --- | --- | --- |
| `RENAME TABLE test.t1 TO test.t2` | Replicate | `test.t1` matches the filter rule |
| `RENAME TABLE test.t1 TO ignore.t1` | Replicate | `test.t1` matches the filter rule |
| `RENAME TABLE ignore.t1 TO ignore.t2` | Ignore | `ignore.t1` does not match the filter rule |
| `RENAME TABLE test.n1 TO test.t1` | Report an error and exit the replication | The old table name `test.n1` does not match the filter rule, but the new table name `test.t1` matches the filter rule. This operation is illegal. In this case, refer to the error message for handling. |
| `RENAME TABLE ignore.t1 TO test.t1` | Report an error and exit the replication | Same reason as above. |
#### Rename multiple tables in a DDL statement

If a DDL statement renames multiple tables, TiCDC replicates the DDL statement only when the **old database name**, **old table names**, and **new database name** all match the filter rule.

In addition, TiCDC does not support the `RENAME TABLE` DDL that swaps the table names. The following is an example.

Assume that the configuration file of your changefeed is as follows:

```toml
[filter]
rules = ['test.t*']
```

TiCDC processes this type of DDL as follows:

| DDL | Whether to replicate | Reason for the handling |
| --- | --- | --- |
| `RENAME TABLE test.t1 TO test.t2, test.t3 TO test.t4` | Replicate | All database names and table names match the filter rule. |
| `RENAME TABLE test.t1 TO test.ignore1, test.t3 TO test.ignore2` | Replicate | The old database name, the old table names, and the new database name match the filter rule. |
| `RENAME TABLE test.t1 TO ignore.t1, test.t2 TO test.t22;` | Report an error | The new database name `ignore` does not match the filter rule. |
| `RENAME TABLE test.t1 TO test.t4, test.t3 TO test.t1, test.t4 TO test.t3;` | Report an error | The `RENAME TABLE` DDL swaps the names of `test.t1` and `test.t3` in one DDL statement, which TiCDC cannot handle correctly. In this case, refer to the error message for handling. |
### DDL statement considerations

When executing cross-database DDL statements (such as `CREATE TABLE db1.t1 LIKE t2`) in the upstream, it is recommended that you explicitly specify all relevant database names in DDL statements (such as `CREATE TABLE db1.t1 LIKE db2.t2`). Otherwise, cross-database DDL statements might not be executed correctly in the downstream due to the lack of database name information.
