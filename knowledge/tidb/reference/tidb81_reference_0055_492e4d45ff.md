# Clustered index concepts, scenarios, and table/index creation behavior

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/clustered-indexes.md`
- Source Title: `Clustered Indexes`
- Source Heading Path: `Clustered Indexes | Clustered Indexes > User scenarios | Clustered Indexes > Usages | Clustered Indexes > Usages > Create a table with clustered indexes | Clustered Indexes > Usages > Add or drop clustered indexes | Clustered Indexes > Usages > Add or drop non-clustered indexes`
- Source Line Ranges: `5-92`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `clustered-index`, `primary-key`, `storage-layout`, `create-table`, `alter-table`, `system-variable`, `limitations`, `performance`, `write-hotspot`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0055_492e4d45ff`
- Source ID: `tidb-docs-8.1:clustered-indexes.md#clustered-indexes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4cebd30417beb0dd9dea6b6c467301e384f7979987afdc058e280d9e357723e5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/clustered-indexes#clustered-indexes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/clustered-indexes.md

## Retrieval Guidance

- Use When: Use this chunk when you need the TiDB clustered index definition, performance scenarios, storage layout differences, CREATE TABLE syntax, default behavior of @@global.tidb_enable_clustered_index, or the stated limitations on adding and dropping clustered indexes.
- Retrieval Keywords: clustered index, non-clustered index, NONCLUSTERED, CLUSTERED, PRIMARY KEY, _tidb_rowid, index-organized table, IOT, CREATE TABLE ... PRIMARY KEY CLUSTERED, CREATE TABLE ... PRIMARY KEY NONCLUSTERED, /*T![clustered_index] CLUSTERED */, /*T![clustered_index] NONCLUSTERED */, @@global.tidb_enable_clustered_index, OFF, ON, INT_ONLY, alter-primary-key, ALTER TABLE t ADD PRIMARY KEY(b, a) CLUSTERED, ALTER TABLE t DROP PRIMARY KEY, ALTER TABLE t DROP INDEX `PRIMARY`, ALTER TABLE t ADD PRIMARY KEY(b, a) NONCLUSTERED, write hotspot, secondary indexes
- Follow-up Guidance: The source also shows how to check whether a table primary key is CLUSTERED or NONCLUSTERED by using SHOW CREATE TABLE, SHOW INDEX FROM, or information_schema.tables.TIDB_PK_TYPE.
- Classification Note: This is reference content because it explains clustered index concepts, storage behavior, supported SQL syntax, system variable defaults, and documented limitations for TiDB tables with primary keys.

## Official Source Content

# Clustered Indexes

TiDB supports the clustered index feature since v5.0. This feature controls how data is stored in tables containing primary keys. It provides TiDB the ability to organize tables in a way that can improve the performance of certain queries.

The term _clustered_ in this context refers to the _organization of how data is stored_ and not _a group of database servers working together_. Some database management systems refer to clustered index tables as _index-organized tables_ (IOT).

Currently, tables containing primary keys in TiDB are divided into the following two categories:

- `NONCLUSTERED`: The primary key of the table is non-clustered index. In tables with non-clustered indexes, the keys for row data consist of internal [`_tidb_rowid`](https://docs.pingcap.com/tidb/stable/tidb-rowid) values implicitly assigned by TiDB. Because primary keys are essentially unique indexes, tables with non-clustered indexes need at least two key-value pairs to store a row, which are:
    - `_tidb_rowid` (key) - row data (value)
    - Primary key data (key) - `_tidb_rowid` (value)
- `CLUSTERED`: The primary key of the table is clustered index. In tables with clustered indexes, the keys for row data consist of primary key data given by the user. Therefore, tables with clustered indexes need only one key-value pair to store a row, which is:
    - Primary key data (key) - row data (value)

> **Note:**
>
> TiDB supports clustering only by a table's `PRIMARY KEY`. With clustered indexes enabled, the terms _the_ `PRIMARY KEY` and _the clustered index_ might be used interchangeably. `PRIMARY KEY` refers to the constraint (a logical property), and clustered index describes the physical implementation of how the data is stored.
## User scenarios

Compared to tables with non-clustered indexes, tables with clustered indexes offer greater performance and throughput advantages in the following scenarios:

+ When data is inserted, the clustered index reduces one write of the index data from the network.
+ When a query with an equivalent condition only involves the primary key, the clustered index reduces one read of index data from the network.
+ When a query with a range condition only involves the primary key, the clustered index reduces multiple reads of index data from the network.
+ When a query with an equivalent or range condition only involves the primary key prefix, the clustered index reduces multiple reads of index data from the network.

On the other hand, tables with clustered indexes have certain disadvantages. See the following:

- There might be write hotspot issues when inserting a large number of primary keys with close values.
- The table data takes up more storage space if the data type of the primary key is larger than 64 bits, especially when there are multiple secondary indexes.
## Usages
### Create a table with clustered indexes

Since TiDB v5.0, you can add non-reserved keywords `CLUSTERED` or `NONCLUSTERED` after `PRIMARY KEY` in a `CREATE TABLE` statement to specify whether the table's primary key is a clustered index. For example:

```sql
CREATE TABLE t (a BIGINT PRIMARY KEY CLUSTERED, b VARCHAR(255));
CREATE TABLE t (a BIGINT PRIMARY KEY NONCLUSTERED, b VARCHAR(255));
CREATE TABLE t (a BIGINT KEY CLUSTERED, b VARCHAR(255));
CREATE TABLE t (a BIGINT KEY NONCLUSTERED, b VARCHAR(255));
CREATE TABLE t (a BIGINT, b VARCHAR(255), PRIMARY KEY(a, b) CLUSTERED);
CREATE TABLE t (a BIGINT, b VARCHAR(255), PRIMARY KEY(a, b) NONCLUSTERED);
```

Note that keywords `KEY` and `PRIMARY KEY` have the same meaning in the column definition.

You can also use the [comment syntax](https://docs.pingcap.com/tidb/stable/comment-syntax) in TiDB to specify the type of the primary key. For example:

```sql
CREATE TABLE t (a BIGINT PRIMARY KEY /*T![clustered_index] CLUSTERED */, b VARCHAR(255));
CREATE TABLE t (a BIGINT PRIMARY KEY /*T![clustered_index] NONCLUSTERED */, b VARCHAR(255));
CREATE TABLE t (a BIGINT, b VARCHAR(255), PRIMARY KEY(a, b) /*T![clustered_index] CLUSTERED */);
CREATE TABLE t (a BIGINT, b VARCHAR(255), PRIMARY KEY(a, b) /*T![clustered_index] NONCLUSTERED */);
```

For statements that do not explicitly specify the keyword `CLUSTERED`/`NONCLUSTERED`, the default behavior is controlled by the system variable [`@@global.tidb_enable_clustered_index`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_clustered_index-new-in-v50). Supported values for this variable are as follows:

- `OFF` indicates that primary keys are created as non-clustered indexes by default.
- `ON` indicates that primary keys are created as clustered indexes by default.
- `INT_ONLY` indicates that the behavior is controlled by the configuration item `alter-primary-key`. If `alter-primary-key` is set to `true`, primary keys are created as non-clustered indexes by default. If it is set to `false`, only the primary keys which consist of an integer column are created as clustered indexes.

The default value of `@@global.tidb_enable_clustered_index` is `ON`.
### Add or drop clustered indexes

TiDB does not support adding or dropping clustered indexes after tables are created. Nor does it support the mutual conversion between clustered indexes and non-clustered indexes. For example:

```sql
ALTER TABLE t ADD PRIMARY KEY(b, a) CLUSTERED; -- Currently not supported.
ALTER TABLE t DROP PRIMARY KEY;     -- If the primary key is a clustered index, then not supported.
ALTER TABLE t DROP INDEX `PRIMARY`; -- If the primary key is a clustered index, then not supported.
```
### Add or drop non-clustered indexes

TiDB supports adding or dropping non-clustered indexes after tables are created. You can explicitly specify the keyword `NONCLUSTERED` or omit it. For example:

```sql
ALTER TABLE t ADD PRIMARY KEY(b, a) NONCLUSTERED;
ALTER TABLE t ADD PRIMARY KEY(b, a); -- If you omit the keyword, the primary key is a non-clustered index by default.
ALTER TABLE t DROP PRIMARY KEY;
ALTER TABLE t DROP INDEX `PRIMARY`;
```
