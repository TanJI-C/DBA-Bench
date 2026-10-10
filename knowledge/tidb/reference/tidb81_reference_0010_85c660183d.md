# TiDB feature support matrix for core SQL, data types, indexing, and storage features

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/basic-features.md`
- Source Title: `TiDB Features`
- Source Heading Path: `TiDB Features | TiDB Features > Data types, functions, and operators | TiDB Features > Indexing and constraints | TiDB Features > SQL statements`
- Source Line Ranges: `5-90`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tiflash`, `tikv`, `sql`
- Topic Tags: `feature-matrix`, `version-support`, `data-types`, `functions`, `operators`, `indexes`, `constraints`, `sql-statements`, `storage-engine`, `experimental-features`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0010_85c660183d`
- Source ID: `tidb-docs-8.1:basic-features.md#tidb-features`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `dafb0a1d46e68f46a8b976dd310cffa80dfe329b3673b3c86b116fb8260e05ee`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/basic-features#tidb-features
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/basic-features.md

## Retrieval Guidance

- Use When: Use this chunk when you need the TiDB 8.1 feature support matrix for data types, functions and operators, indexing and constraints, or SQL statements across versions 8.1 to 5.1.
- Retrieval Keywords: TiDB Features, feature support matrix, 8.1 7.5 7.1 6.5 6.1 5.4 5.3 5.2 5.1, Y N E meanings, Long-Term Support LTS, Development Milestone Release DMR, JSON type, JSON functions, User-level lock, Expression indexes, Columnar storage TiFlash, Use FastScan to accelerate queries in OLAP scenarios, RocksDB engine, Titan plugin, Titan Level Merge, Use buckets to improve scan concurrency, Invisible indexes, Composite PRIMARY KEY, CHECK constraints, Unique indexes, Clustered index on integer PRIMARY KEY, Clustered index on composite or non-integer key, Multi-valued indexes, Foreign key, TiFlash late materialization, Basic SELECT INSERT UPDATE DELETE REPLACE, INSERT ON DUPLICATE KEY UPDATE, LOAD DATA INFILE, SELECT INTO OUTFILE, EXCEPT and INTERSECT operators, Common Table Expressions CTE, EXPLAIN ANALYZE, User-defined variables, BATCH ON COLUMN LIMIT INTEGER DELETE, BATCH ON COLUMN LIMIT INTEGER INSERT UPDATE REPLACE, ALTER TABLE ... COMPACT, Table Lock, TiFlash Query Result Materialization
- Follow-up Guidance: The source also states that Y means generally available, N means not supported, and E means experimental with usage limitations and subject to change or removal.
- Classification Note: This chunk is reference content because it is a version-by-version matrix listing whether specific TiDB features are GA, unsupported, or experimental.

## Official Source Content

# TiDB Features

This document lists the features supported in different TiDB versions, including [Long-Term Support (LTS)](https://docs.pingcap.com/tidb/stable/releases/versioning#long-term-support-releases) versions and [Development Milestone Release (DMR)](https://docs.pingcap.com/tidb/stable/releases/versioning#development-milestone-releases) versions after the latest LTS version.

You can try out TiDB features on [TiDB Playground](https://play.tidbcloud.com/?utm_source=docs&utm_medium=tidb_features).

> **Note:**
>
> PingCAP does not provide patch releases for DMR versions. Any bugs will be fixed in future releases. For general purposes, it is recommended to use the [latest LTS version](https://docs.pingcap.com/tidb/stable).
>
> The abbreviations in the table below have the following meanings:
>
> - Y: the feature is generally available (GA) and can be used in production environments. Note that even if a feature is GA in a DMR version, it is recommended to use the feature in production environments in a later LTS version.
> - N: the feature is not supported.
> - E: the feature is not GA yet (experimental) and you need to be aware of the usage limitations. Experimental features are subject to change or removal without prior notice. The syntax and implementation might be modified before the general availability. If you encounter any problems, you can report an [issue](https://github.com/pingcap/tidb/issues) on GitHub.
## Data types, functions, and operators

| Data types, functions, and operators | 8.1 | 7.5 | 7.1 | 6.5 | 6.1 | 5.4 | 5.3 | 5.2 | 5.1 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| [Numeric types](https://docs.pingcap.com/tidb/stable/data-type-numeric) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [Date and time types](https://docs.pingcap.com/tidb/stable/data-type-date-and-time) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [String types](https://docs.pingcap.com/tidb/stable/data-type-string) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [JSON type](https://docs.pingcap.com/tidb/stable/data-type-json) | Y | Y | Y | Y | E | E | E | E | E |
| [Control flow functions](https://docs.pingcap.com/tidb/stable/functions-and-operators/control-flow-functions) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [String functions](https://docs.pingcap.com/tidb/stable/functions-and-operators/string-functions) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [Numeric functions and operators](https://docs.pingcap.com/tidb/stable/functions-and-operators/numeric-functions-and-operators) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [Date and time functions](https://docs.pingcap.com/tidb/stable/functions-and-operators/date-and-time-functions) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [Bit functions and operators](https://docs.pingcap.com/tidb/stable/functions-and-operators/bit-functions-and-operators) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [Cast functions and operators](https://docs.pingcap.com/tidb/stable/functions-and-operators/cast-functions-and-operators) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [Encryption and compression functions](https://docs.pingcap.com/tidb/stable/functions-and-operators/encryption-and-compression-functions) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [Information functions](https://docs.pingcap.com/tidb/stable/functions-and-operators/information-functions) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [JSON functions](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions) | Y | Y | Y | Y | E | E | E | E | E |
| [Aggregation functions](https://docs.pingcap.com/tidb/stable/functions-and-operators/aggregate-group-by-functions) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [Window functions](https://docs.pingcap.com/tidb/stable/functions-and-operators/window-functions) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [Miscellaneous functions](https://docs.pingcap.com/tidb/stable/functions-and-operators/miscellaneous-functions) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [Operators](https://docs.pingcap.com/tidb/stable/functions-and-operators/operators) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [Character sets and collations](https://docs.pingcap.com/tidb/stable/character-set-and-collation) [^1] | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [User-level lock](https://docs.pingcap.com/tidb/stable/functions-and-operators/locking-functions) | Y | Y | Y | Y | Y | N | N | N | N |
## Indexing and constraints

| Indexing and constraints | 8.1 | 7.5 | 7.1 | 6.5 | 6.1 | 5.4 | 5.3 | 5.2 | 5.1 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| [Expression indexes](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-index#expression-index) [^2] | Y | Y | Y | Y | E | E | E | E | E |
| [Columnar storage (TiFlash)](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-overview) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [Use FastScan to accelerate queries in OLAP scenarios](https://docs.pingcap.com/tidb/stable/tiflash/use-fastscan) | Y | Y | Y | E | N | N | N | N | N |
| [RocksDB engine](https://docs.pingcap.com/tidb/stable/storage-engine/rocksdb-overview) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [Titan plugin](https://docs.pingcap.com/tidb/stable/storage-engine/titan-overview) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [Titan Level Merge](https://docs.pingcap.com/tidb/stable/storage-engine/titan-configuration#level-merge-experimental) | E | E | E | E | E | E | E | E | E |
| [Use buckets to improve scan concurrency](https://docs.pingcap.com/tidb/stable/tune-region-performance#use-bucket-to-increase-concurrency) | E | E | E | E | E | N | N | N | N |
| [Invisible indexes](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-index#invisible-index) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [Composite `PRIMARY KEY`](https://docs.pingcap.com/tidb/stable/constraints) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [`CHECK` constraints](https://docs.pingcap.com/tidb/stable/constraints#check) | Y | Y | N | N | N | N | N | N | N |
| [Unique indexes](https://docs.pingcap.com/tidb/stable/constraints) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [Clustered index on integer `PRIMARY KEY`](https://docs.pingcap.com/tidb/stable/clustered-indexes) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [Clustered index on composite or non-integer key](https://docs.pingcap.com/tidb/stable/clustered-indexes) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [Multi-valued indexes](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-index#multi-valued-indexes) | Y | Y | Y | N | N | N | N | N | N |
| [Foreign key](https://docs.pingcap.com/tidb/stable/constraints#foreign-key) | E | E | E | N | N | N | N | N | N |
| [TiFlash late materialization](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-late-materialization) | Y | Y | Y | N | N | N | N | N | N |
## SQL statements

| SQL statements [^3] | 8.1 | 7.5 | 7.1 | 6.5 | 6.1 | 5.4 | 5.3 | 5.2 | 5.1 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Basic `SELECT`, `INSERT`, `UPDATE`, `DELETE`, `REPLACE` | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| `INSERT ON DUPLICATE KEY UPDATE` | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| `LOAD DATA INFILE` | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| `SELECT INTO OUTFILE` | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| `INNER JOIN`, <code>LEFT\|RIGHT [OUTER] JOIN</code> | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| `UNION`, `UNION ALL` | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [`EXCEPT` and `INTERSECT` operators](https://docs.pingcap.com/tidb/stable/functions-and-operators/set-operators) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| `GROUP BY`, `ORDER BY` | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [Window Functions](https://docs.pingcap.com/tidb/stable/functions-and-operators/window-functions) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [Common Table Expressions (CTE)](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-with) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| `START TRANSACTION`, `COMMIT`, `ROLLBACK` | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [`EXPLAIN`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-explain) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [`EXPLAIN ANALYZE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-explain-analyze) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [User-defined variables](https://docs.pingcap.com/tidb/stable/user-defined-variables) | E | E | E | E | E | E | E | E | E |
| [`BATCH [ON COLUMN] LIMIT INTEGER DELETE`](/sql-statements/sql-statement-batch.md) | Y | Y | Y | Y | Y | N | N | N | N |
| [`BATCH [ON COLUMN] LIMIT INTEGER INSERT/UPDATE/REPLACE`](/sql-statements/sql-statement-batch.md) | Y | Y | Y | Y | N | N | N | N | N |
| [`ALTER TABLE ... COMPACT`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-table-compact) | Y | Y | Y | Y | E | N | N | N | N |
| [Table Lock](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-lock-tables-and-unlock-tables) | E | E | E | E | E | E | E | E | E |
| [TiFlash Query Result Materialization](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-results-materialization) | Y | Y | Y | E | N | N | N | N | N |
