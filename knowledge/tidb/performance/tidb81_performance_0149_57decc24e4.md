# Clustered index feature, configuration, and limitations

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.0.0.md`
- Source Title: `What's New in TiDB 5.0`
- Source Heading Path: `What's New in TiDB 5.0 > Performance optimization > Clustered index`
- Source Line Ranges: `174-234`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `clustered-index`, `primary-key`, `table-design`, `system-variables`, `limitations`, `compatibility`, `rollback`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0149_57decc24e4`
- Source ID: `tidb-docs-8.1:releases/release-5.0.0.md#clustered-index`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2bca7addcd028946b379a5c5ee5712ff253b56037d0157be9f81bcf9cc9f5cc6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.0.0#clustered-index
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.0.0.md

## Retrieval Guidance

- Use When: Use this content when you need release notes about clustered index behavior, creation syntax, system variable control, performance effects, or feature limitations in TiDB 5.0.
- Retrieval Keywords: clustered index, CLUSTERED, NONCLUSTERED, PRIMARY KEY CLUSTERED, SHOW INDEX FROM tbl-name, tidb_enable_clustered_index, INT_ONLY, alter-primary-key, ROWID, CREATE TABLE `t` (`a` VARCHAR(255), `b` INT, PRIMARY KEY (`a`, `b`) CLUSTERED), TiDB Binlog, SHARD_ROW_ID_BITS, PRE_SPLIT_REGIONS, dropping clustered indexes is not supported
- Follow-up Guidance: The content also points to checking whether a table has a clustered index with `SHOW INDEX FROM tbl-name` and notes rollback handling for newly-added tables after an upgrade.
- Classification Note: This is classified as performance content because it explains how clustered indexes reduce network I/O for inserts and primary-key queries and states significant performance improvement when the feature is enabled.

## Official Source Content

### Clustered index

[User document](https://docs.pingcap.com/tidb/stable/clustered-indexes), [#4841](https://github.com/pingcap/tidb/issues/4841)

When you are designing table structures or analyzing database behaviors, it is recommended to use the clustered index feature if you find that some columns with primary keys are often grouped and sorted, queries on these columns often return a certain range of data or a small amount of data with different values, and the corresponding data does not cause read or write hotspot issues.

Clustered indexes is a storage structure associated with the data of a table. Some database management systems refer to clustered index tables as _index-organized tables_. When creating a clustered index, you can specify one or more columns from the table as the keys for the index. TiDB stores these keys in a specific structure, which allows TiDB to quickly and efficiently find the rows associated with the keys, thus improves the performance of querying and writing data.

When the clustered index feature is enabled, the TiDB performance improves significantly (for example in the TPC-C tpmC test, the performance of TiDB, with clustered index enabled, improves by 39%) in the following cases:

+ When data is inserted, the clustered index reduces one write of the index data from the network.
+ When a query with an equivalent condition only involves the primary key, the clustered index reduces one read of index data from the network.
+ When a query with a range condition only involves the primary key, the clustered index reduces multiple reads of index data from the network.
+ When a query with an equivalent or range condition involves the primary key prefix, the clustered index reduces multiple reads of index data from the network.

Each table can either use a clustered or non-clustered index to sort and store data. The differences of these two storage structures are as follows:

+ When creating a clustered index, you can specify one or more columns in the table as the key value of the index. A clustered index sorts and stores the data of a table according to the key value. Each table can have only one clustered index. If a table has a clustered index, it is called a clustered index table. Otherwise, it is called a non-clustered index table.
+ When you create a non-clustered index, the data in the table is stored in an unordered structure. You do not need to explicitly specify the key value of the non-clustered index, because TiDB automatically assigns a unique ROWID to each row of data. During a query, the ROWID is used to locate the corresponding row. Because there are at least two network I/O operations when you query or insert data, the performance is degraded compared with clustered indexes.

When table data is modified, the database system automatically maintains clustered indexes and non-clustered indexes for you.

All primary keys are created as non-clustered indexes by default. You can create a primary key as a clustered index or non-clustered index in either of the following two ways:

+ Specify the keyword `CLUSTERED | NONCLUSTERED` in the statement when creating a table, then the system creates the table in the specified way. The syntax is as follows:

```sql
CREATE TABLE `t` (`a` VARCHAR(255), `b` INT, PRIMARY KEY (`a`, `b`) CLUSTERED);
```

Or

```sql
CREATE TABLE `t` (`a` VARCHAR(255) PRIMARY KEY CLUSTERED, `b` INT);
```

You can execute the statement `SHOW INDEX FROM tbl-name` to query whether a table has a clustered index.

+ Configure the system variable `tidb_enable_clustered_index` to control the clustered index feature. Supported values are `ON`, `OFF`, and `INT_ONLY`.
    + `ON`: Indicates that the clustered index feature is enabled for all types of primary keys. Adding and dropping non-clustered indexes are supported.
    + `OFF`: Indicates that the clustered index feature is disabled for all types of primary keys. Adding and dropping non-clustered indexes are supported.
    + `INT_ONLY`: The default value. If the variable is set to `INT_ONLY` and `alter-primary-key` is set to `false`, the primary keys which consist of single integer columns are created as clustered indexes by default. The behavior is consistent with that of TiDB v5.0 and earlier versions.

If a `CREATE TABLE` statement contains the keyword `CLUSTERED | NONCLUSTERED`, the statement overrides the configuration of the system variable and the configuration item.

You are recommended to use the clustered index feature by specifying the keyword `CLUSTERED | NONCLUSTERED` in statements. In this way, it is more flexible for TiDB to use all data types of clustered and non-clustered indexes in the system at the same time as required.

It is not recommended to use `tidb_enable_clustered_index = INT_ONLY`, because `INT_ONLY` is temporarily used to make this feature compatible and will be deprecated in the future.

Limitations for the clustered index are as follows:

+ Mutual conversion between clustered indexes and non-clustered indexes is not supported.
+ Dropping clustered indexes is not supported.
+ Adding, dropping, and altering clustered indexes using `ALTER TABLE` statements are not supported.
+ Reorganizing and re-creating a clustered index is not supported.
+ Enabling or disabling indexes is not supported, which means the invisible index feature is not effective for clustered indexes.
+ Creating a `UNIQUE KEY` as a clustered index is not supported.
+ Using the clustered index feature together with TiDB Binlog is not supported. After TiDB Binlog is enabled, TiDB only supports creating a single integer primary key as a clustered index. TiDB Binlog does not replicate data changes of existing tables with clustered indexes to the downstream.
+ Using the clustered index feature together with the attributes `SHARD_ROW_ID_BITS` and `PRE_SPLIT_REGIONS` is not supported.
+ If the cluster is upgraded to a later version then rolls back, you need to downgrade newly-added tables by exporting table data before the rollback and importing the data after the rollback. Other tables are not affected.
