# CREATE INDEX invisible indexes variables compatibility and references

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-create-index.md`
- Source Title: `CREATE INDEX | TiDB SQL Statement Reference`
- Source Heading Path: `CREATE INDEX > Invisible index | CREATE INDEX > Associated system variables | CREATE INDEX > MySQL compatibility | CREATE INDEX > See also`
- Source Line Ranges: `358-395`
- Source Scope: `all`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `create-index`, `invisible-indexes`, `optimizer`, `system-variables`, `mysql-compatibility`, `expression-indexes`, `spm`, `references`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0555_5c04f7ea95`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-create-index.md#invisible-index`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5ee1dd7c268408b76544779f290126472eaf92c155ef627376b3667aa36fdba1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-index#invisible-index
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-create-index.md

## Retrieval Guidance

- Use When: Use this chunk when looking for CREATE INDEX behavior of invisible indexes, related system variables, MySQL compatibility notes, and linked reference topics.
- Retrieval Keywords: Invisible index, CREATE UNIQUE INDEX c1 ON t1 (c1) INVISIBLE, tidb_opt_use_invisible_indexes, ALTER INDEX, Associated system variables CREATE INDEX, tidb_ddl_enable_fast_reorg, tidb_ddl_reorg_worker_cnt, tidb_ddl_reorg_batch_size, tidb_enable_auto_increment_in_generated, tidb_ddl_reorg_priority, MySQL compatibility CREATE INDEX, FULLTEXT syntax parsed but not supported, HASH BTREE RTREE ignored, Descending indexes are not supported, CLUSTERED primary key add not supported, Expression indexes incompatible with views, expression indexes compatibility issues with bindings, SQL Plan Management SPM, multi-valued indexes exact data type writes fail
- Follow-up Guidance: The source links to ALTER INDEX, Index Selection, Wrong Index Solution, ADD INDEX, DROP INDEX, RENAME INDEX, ADD COLUMN, CREATE TABLE, and EXPLAIN for related details.
- Classification Note: This is reference content because it summarizes invisible index semantics, names the associated system variables, and lists compatibility constraints and related references for CREATE INDEX.

## Official Source Content

## Invisible index

By default, invisible indexes are indexes that are ignored by the query optimizer:

```sql
CREATE TABLE t1 (c1 INT, c2 INT, UNIQUE(c2));
CREATE UNIQUE INDEX c1 ON t1 (c1) INVISIBLE;
```

Starting from TiDB v8.0.0, you can make the optimizer select invisible indexes by modifying the system variable [`tidb_opt_use_invisible_indexes`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_use_invisible_indexes-new-in-v800).

For details, see [`ALTER INDEX`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-index).
## Associated system variables

The system variables associated with the `CREATE INDEX` statement are `tidb_ddl_enable_fast_reorg`, `tidb_ddl_reorg_worker_cnt`, `tidb_ddl_reorg_batch_size`, `tidb_enable_auto_increment_in_generated`, and `tidb_ddl_reorg_priority`. Refer to [system variables](https://docs.pingcap.com/tidb/stable/system-variables#tidb_ddl_reorg_worker_cnt) for details.
## MySQL compatibility

* TiDB supports parsing the `FULLTEXT` syntax but does not support using the `FULLTEXT`, `HASH`, and `SPATIAL` indexes.
* TiDB accepts index types such as `HASH`, `BTREE` and `RTREE` in syntax for compatibility with MySQL, but ignores them.
* Descending indexes are not supported (similar to MySQL 5.7).
* Adding the primary key of the `CLUSTERED` type to a table is not supported. For more details about the primary key of the `CLUSTERED` type, refer to [clustered index](https://docs.pingcap.com/tidb/stable/clustered-indexes).
* Expression indexes are incompatible with views. When a query is executed using a view, the expression index cannot be used at the same time.
* Expression indexes have compatibility issues with bindings. When the expression of an expression index has a constant, the binding created for the corresponding query expands its scope. For example, suppose that the expression in the expression index is `a+1`, and the corresponding query condition is `a+1 > 2`. In this case, the created binding is `a+? > ?`, which means that the query with the condition such as `a+2 > 2` is also forced to use the expression index and results in a poor execution plan. In addition, this also affects the baseline capturing and baseline evolution in SQL Plan Management (SPM).
* The data written with multi-valued indexes must exactly match the defined data type. Otherwise, data writes fail. For details, see [create multi-valued indexes](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-index#create-multi-valued-indexes).
## See also

* [Index Selection](https://docs.pingcap.com/tidb/stable/choose-index)
* [Wrong Index Solution](https://docs.pingcap.com/tidb/stable/wrong-index-solution)
* [ADD INDEX](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-add-index)
* [DROP INDEX](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-index)
* [RENAME INDEX](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-rename-index)
* [ALTER INDEX](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-index)
* [ADD COLUMN](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-add-column)
* [CREATE TABLE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-table)
* [EXPLAIN](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-explain)
