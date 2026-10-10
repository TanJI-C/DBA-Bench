# Foreign key metadata and execution plan inspection

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/foreign-key.md`
- Source Title: `FOREIGN KEY Constraints`
- Source Heading Path: `FOREIGN KEY Constraints > Definition and metadata of foreign keys | FOREIGN KEY Constraints > View execution plans with foreign keys`
- Source Line Ranges: `185-284`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `foreign-keys`, `metadata`, `show-create-table`, `information-schema`, `execution-plans`, `explain`, `explain-analyze`, `constraint-check`, `cascade`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0286_f61b6a9fa1`
- Source ID: `tidb-docs-8.1:foreign-key.md#definition-and-metadata-of-foreign-keys`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6c19880a404f726c15c701eea690bc97cacfa5dad059542affba9b60bcca1353`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/foreign-key#definition-and-metadata-of-foreign-keys
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/foreign-key.md

## Retrieval Guidance

- Use When: Use this chunk when you need to inspect foreign key definitions in table metadata or identify foreign key operators in execution plans for DML statements.
- Retrieval Keywords: SHOW CREATE TABLE, INFORMATION_SCHEMA.KEY_COLUMN_USAGE, INFORMATION_SCHEMA.TABLE_CONSTRAINTS, INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS, SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME, CONSTRAINT_NAME FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE WHERE REFERENCED_TABLE_SCHEMA IS NOT NULL, CONSTRAINT_TYPE='FOREIGN KEY', EXPLAIN, EXPLAIN ANALYZE, Foreign_Key_Check, Foreign_Key_Cascade, foreign_key:fk_1, check_exist, on_delete:CASCADE, table:parent, table:child, index:idx_pid
- Follow-up Guidance: The source also shows example queries against KEY_COLUMN_USAGE, TABLE_CONSTRAINTS, and REFERENTIAL_CONSTRAINTS, plus EXPLAIN and EXPLAIN ANALYZE output with Foreign_Key_Check and Foreign_Key_Cascade operators.
- Classification Note: This is reference content because it documents how to view foreign key metadata and execution plan details using specific SQL statements, system tables, and plan operators.

## Official Source Content

## Definition and metadata of foreign keys

To view the definition of a foreign key constraint, execute the [`SHOW CREATE TABLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-create-table) statement:

```sql
mysql> SHOW CREATE TABLE child\G
*************************** 1. row ***************************
       Table: child
Create Table: CREATE TABLE `child` (
  `id` int(11) DEFAULT NULL,
  `pid` int(11) DEFAULT NULL,
  KEY `idx_pid` (`pid`),
  CONSTRAINT `fk_1` FOREIGN KEY (`pid`) REFERENCES `test`.`parent` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin
```

You can also get information about foreign keys using either of the following system tables:

- [`INFORMATION_SCHEMA.KEY_COLUMN_USAGE`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-key-column-usage)
- [`INFORMATION_SCHEMA.TABLE_CONSTRAINTS`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-table-constraints)
- [`INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-referential-constraints)

The following provides examples:

Get information about foreign keys from the `INFORMATION_SCHEMA.KEY_COLUMN_USAGE` system table:

```sql
mysql> SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME, CONSTRAINT_NAME FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE WHERE REFERENCED_TABLE_SCHEMA IS NOT NULL;
+--------------+---------------+------------------+-----------------+
| TABLE_SCHEMA | TABLE_NAME    | COLUMN_NAME      | CONSTRAINT_NAME |
+--------------+---------------+------------------+-----------------+
| test         | child         | pid              | fk_1            |
| test         | product_order | product_category | fk_1            |
| test         | product_order | product_id       | fk_1            |
| test         | product_order | customer_id      | fk_2            |
+--------------+---------------+------------------+-----------------+
```

Get information about foreign keys from the `INFORMATION_SCHEMA.TABLE_CONSTRAINTS` system table:

```sql
mysql> SELECT * FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS WHERE CONSTRAINT_TYPE='FOREIGN KEY'\G
***************************[ 1. row ]***************************
CONSTRAINT_CATALOG | def
CONSTRAINT_SCHEMA  | test
CONSTRAINT_NAME    | fk_1
TABLE_SCHEMA       | test
TABLE_NAME         | child
CONSTRAINT_TYPE    | FOREIGN KEY
```

Get information about foreign keys from the `INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS` system table:

```sql
mysql> SELECT * FROM INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS\G
***************************[ 1. row ]***************************
CONSTRAINT_CATALOG        | def
CONSTRAINT_SCHEMA         | test
CONSTRAINT_NAME           | fk_1
UNIQUE_CONSTRAINT_CATALOG | def
UNIQUE_CONSTRAINT_SCHEMA  | test
UNIQUE_CONSTRAINT_NAME    | PRIMARY
MATCH_OPTION              | NONE
UPDATE_RULE               | NO ACTION
DELETE_RULE               | CASCADE
TABLE_NAME                | child
REFERENCED_TABLE_NAME     | parent
```
## View execution plans with foreign keys

You can use the `EXPLAIN` statement to view execution plans. The `Foreign_Key_Check` operator performs the foreign key constraint check on DML statements that are executed.

```sql
mysql> explain insert into child values (1,1);
+-----------------------+---------+------+---------------+-------------------------------+
| id                    | estRows | task | access object | operator info                 |
+-----------------------+---------+------+---------------+-------------------------------+
| Insert_1              | N/A     | root |               | N/A                           |
| └─Foreign_Key_Check_3 | 0.00    | root | table:parent  | foreign_key:fk_1, check_exist |
+-----------------------+---------+------+---------------+-------------------------------+
```

You can use the `EXPLAIN ANALYZE` statement to view the execution of the foreign key reference behavior. The `Foreign_Key_Cascade` operator performs foreign key referencing for DML statements that are executed.

```sql
mysql> explain analyze delete from parent where id = 1;
+----------------------------------+---------+---------+-----------+---------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------------------------+-----------+------+
| id                               | estRows | actRows | task      | access object                   | execution info                                                                                                                                                                               | operator info                               | memory    | disk |
+----------------------------------+---------+---------+-----------+---------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------------------------+-----------+------+
| Delete_2                         | N/A     | 0       | root      |                                 | time:117.3µs, loops:1                                                                                                                                                                        | N/A                                         | 380 Bytes | N/A  |
| ├─Point_Get_1                    | 1.00    | 1       | root      | table:parent                    | time:63.6µs, loops:2, Get:{num_rpc:1, total_time:29.9µs}                                                                                                                                     | handle:1                                    | N/A       | N/A  |
| └─Foreign_Key_Cascade_3          | 0.00    | 0       | root      | table:child, index:idx_pid      | total:1.28ms, foreign_keys:1                                                                                                                                                                 | foreign_key:fk_1, on_delete:CASCADE         | N/A       | N/A  |
|   └─Delete_7                     | N/A     | 0       | root      |                                 | time:904.8µs, loops:1                                                                                                                                                                        | N/A                                         | 1.11 KB   | N/A  |
|     └─IndexLookUp_11             | 10.00   | 1       | root      |                                 | time:869.5µs, loops:2, index_task: {total_time: 371.1µs, fetch_handle: 357.3µs, build: 1.25µs, wait: 12.5µs}, table_task: {total_time: 382.6µs, num: 1, concurrency: 5}                      |                                             | 9.13 KB   | N/A  |
|       ├─IndexRangeScan_9(Build)  | 10.00   | 1       | cop[tikv] | table:child, index:idx_pid(pid) | time:351.2µs, loops:3, cop_task: {num: 1, max: 282.3µs, proc_keys: 0, rpc_num: 1, rpc_time: 263µs, copr_cache_hit_ratio: 0.00, distsql_concurrency: 15}, tikv_task:{time:220.2µs, loops:0}   | range:[1,1], keep order:false, stats:pseudo | N/A       | N/A  |
|       └─TableRowIDScan_10(Probe) | 10.00   | 1       | cop[tikv] | table:child                     | time:223.9µs, loops:2, cop_task: {num: 1, max: 168.8µs, proc_keys: 0, rpc_num: 1, rpc_time: 154.5µs, copr_cache_hit_ratio: 0.00, distsql_concurrency: 15}, tikv_task:{time:145.6µs, loops:0} | keep order:false, stats:pseudo              | N/A       | N/A  |
+----------------------------------+---------+---------+-----------+---------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------------------------+-----------+------+
```
