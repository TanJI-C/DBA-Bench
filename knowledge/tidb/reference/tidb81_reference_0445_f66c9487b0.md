# Monitoring, query plan, functions, and DDL compatibility differences

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/mysql-compatibility.md`
- Source Title: `MySQL Compatibility`
- Source Heading Path: `MySQL Compatibility > Differences from MySQL > Performance schema | MySQL Compatibility > Differences from MySQL > Query Execution Plan | MySQL Compatibility > Differences from MySQL > Built-in functions | MySQL Compatibility > Differences from MySQL > DDL operations`
- Source Line Ranges: `136-181`
- Source Scope: `all`
- Primary Component: `tidb`
- Related Components: `cloud`, `sql`, `tiflash`
- Topic Tags: `performance-schema`, `explain`, `optimizer`, `built-in-functions`, `ddl`, `partitioning`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0445_f66c9487b0`
- Source ID: `tidb-docs-8.1:mysql-compatibility.md#performance-schema`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7f20be87597c14258d7da5152983394044d4a5ab8deb27190690f3b1e3a55425`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/mysql-compatibility#performance-schema
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/mysql-compatibility.md

## Retrieval Guidance

- Use When: Use this chunk when comparing TiDB with MySQL for performance schema behavior, EXPLAIN differences, built-in function discovery, or DDL and partition operation restrictions.
- Retrieval Keywords: Performance schema, Prometheus and Grafana, performance schema tables, return empty results, TiDB Cloud, third-party monitoring integrations, Query Execution Plan, EXPLAIN, EXPLAIN FOR, optimizer_switch, read-only, optimizer hints, SHOW BUILTINS, DDL operations, ALTER TABLE, Unsupported operate same column/index, TIFLASH REPLICA, SHARD_ROW_ID_BITS, AUTO_ID_CACHE, Unsupported modify column: type %d not match origin %d, ALGORITHM={INSTANT,INPLACE,COPY}, CLUSTERED, clustered index, HASH|BTREE|RTREE|FULLTEXT, Unsupported partition type %s, treat as normal table, SUBPARTITION, CHECK PARTITION, OPTIMIZE PARTITION, REPAIR PARTITION, IMPORT PARTITION, DISCARD PARTITION, REBUILD PARTITION, ADD, DROP, TRUNCATE, REORGANIZE, COALESCE
- Follow-up Guidance: The source points to Understand the Query Execution Plan, SHOW BUILTINS, ALTER TABLE, clustered index, and Partitioning for detailed explanations.
- Classification Note: This is a reference chunk because it summarizes compatibility differences in monitoring, query plans, functions, and DDL semantics, including exact errors and syntax handling.

## Official Source Content

### Performance schema

TiDB utilizes a combination of [Prometheus and Grafana](https://docs.pingcap.com/tidb/stable/tidb-monitoring-api) for storing and querying performance monitoring metrics. In TiDB, most [performance schema tables](https://docs.pingcap.com/tidb/stable/performance-schema/performance-schema) do not return any results.

To check performance metrics in TiDB Cloud, you can either check the cluster overview page in the TiDB Cloud console or use [third-party monitoring integrations](https://docs.pingcap.com/tidb/stable/tidb-cloud/third-party-monitoring-integrations). Most [performance schema tables](https://docs.pingcap.com/tidb/stable/performance-schema/performance-schema) return empty results in TiDB.
### Query Execution Plan

The output format, content, and privilege settings of Query Execution Plan (`EXPLAIN`/`EXPLAIN FOR`) in TiDB differ significantly from those in MySQL.

In TiDB, the MySQL system variable `optimizer_switch` is read-only and has no effect on query plans. Although optimizer hints can be used in similar syntax to MySQL, the available hints and their implementation might differ.

For more information, refer to [Understand the Query Execution Plan](https://docs.pingcap.com/tidb/stable/explain-overview).
### Built-in functions

TiDB supports most of the built-in functions in MySQL, but not all. You can use the statement [`SHOW BUILTINS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-builtins) to get a list of the available functions.
### DDL operations

In TiDB, all supported DDL changes can be performed online. However, there are some major restrictions on DDL operations in TiDB compared to MySQL:

* When using a single `ALTER TABLE` statement to alter multiple schema objects (such as columns or indexes) of a table, specifying the same object in multiple changes is not supported. For example, if you execute the `ALTER TABLE t1 MODIFY COLUMN c1 INT, DROP COLUMN c1` command, the `Unsupported operate same column/index` error is output.
* It is not supported to modify multiple TiDB-specific schema objects using a single `ALTER TABLE` statement, such as `TIFLASH REPLICA`, `SHARD_ROW_ID_BITS`, and `AUTO_ID_CACHE`.
* TiDB does not support the changes of some data types using `ALTER TABLE`. For example, TiDB does not support the change from the `DECIMAL` type to the `DATE` type. If a data type change is unsupported, TiDB reports the `Unsupported modify column: type %d not match origin %d` error. Refer to [`ALTER TABLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-modify-column) for more details.
* The `ALGORITHM={INSTANT,INPLACE,COPY}` syntax functions only as an assertion in TiDB, and does not modify the `ALTER` algorithm. See [`ALTER TABLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-table) for further details.
* Adding/Dropping the primary key of the `CLUSTERED` type is unsupported. For more details about the primary key of the `CLUSTERED` type, refer to [clustered index](https://docs.pingcap.com/tidb/stable/clustered-indexes).
* Different types of indexes (`HASH|BTREE|RTREE|FULLTEXT`) are not supported, and will be parsed and ignored when specified.
* TiDB supports `HASH`, `RANGE`, `LIST`, and `KEY` partitioning types. For an unsupported partition type, TiDB returns `Warning: Unsupported partition type %s, treat as normal table`, where `%s` is the specific unsupported partition type.
* Range, Range COLUMNS, List, and List COLUMNS partitioned tables support `ADD`, `DROP`, `TRUNCATE`, and `REORGANIZE` operations. Other partition operations are ignored.
* Hash and Key partitioned tables support `ADD`, `COALESCE`, and `TRUNCATE` operations. Other partition operations are ignored.
* The following syntaxes are not supported for partitioned tables:

    - `SUBPARTITION`
    - `{CHECK|OPTIMIZE|REPAIR|IMPORT|DISCARD|REBUILD} PARTITION`

    For more details on partitioning, see [Partitioning](https://docs.pingcap.com/tidb/stable/partitioned-table).
