# DM overview, limits, and business-side schema design practices

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-best-practices.md`
- Source Title: `TiDB Data Migration (DM) Best Practices`
- Source Heading Path: `TiDB Data Migration (DM) Best Practices | TiDB Data Migration (DM) Best Practices > Performance limitations | TiDB Data Migration (DM) Best Practices > Before data migration | TiDB Data Migration (DM) Best Practices > Before data migration > Best practices for the business side | TiDB Data Migration (DM) Best Practices > Before data migration > Best practices for the business side > Business impact of AUTO_INCREMENT in schema design | TiDB Data Migration (DM) Best Practices > Before data migration > Best practices for the business side > Usage of clustered indexes`
- Source Line Ranges: `5-79`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tidb`, `sql`
- Topic Tags: `overview`, `performance-limits`, `migration-planning`, `schema-design`, `auto_increment`, `clustered-indexes`, `auto_random`, `shard_row_id_bit`, `sequence`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0020_925804c4f4`
- Source ID: `tidb-docs-8.1:dm/dm-best-practices.md#tidb-data-migration-dm-best-practices`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `67557fa3d91a0d516e1d063454bc00a1d34dc6be08357ed1a37bfc0e33acc366`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-best-practices#tidb-data-migration-dm-best-practices
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-best-practices.md

## Retrieval Guidance

- Use When: Use this chunk when planning DM migration to TiDB and evaluating DM performance limits together with schema design choices involving AUTO_INCREMENT, clustered indexes, AUTO_RANDOM, SHARD_ROW_ID_BIT, or SEQUENCE.
- Retrieval Keywords: TiDB Data Migration (DM) Best Practices, DM performance limitations, Max work nodes 1000, Max task number 600, 30k QPS/worker, 20 MB/s/worker, AUTO_INCREMENT, MySQL-compatible AUTO_INCREMENT mode, SEQUENCE function, clustered indexes, non-clustered indexes, SHARD_ROW_ID_BIT, AUTO_RANDOM, write hotspot problems, CREATE TABLE t (a bigint PRIMARY KEY AUTO_RANDOM, b varchar(255)), Select a, a<<6 ,b from t order by a <<6 desc
- Follow-up Guidance: The source also points to deployment architecture planning for long-term DM replication use and compares schema options for write-intensive and read-only scenarios.
- Classification Note: This is classified as architecture because the content describes DM capacity limits and migration-time schema design tradeoffs that affect distributed database behavior and workload distribution.

## Official Source Content

# TiDB Data Migration (DM) Best Practices

[TiDB Data Migration (DM)](https://github.com/pingcap/tiflow/tree/release-8.1/dm) is a data migration tool developed by PingCAP. It supports full and incremental data migration from MySQL-compatible databases such as MySQL, Percona MySQL, MariaDB, Amazon RDS for MySQL, and Amazon Aurora into TiDB.

You can use DM in the following scenarios:

- Perform full and incremental data migration from a single MySQL-compatible database instance to TiDB
- Migrate and merge MySQL shards of small datasets (less than 1 TiB) to TiDB
- In the data hub scenario, such as the middle platform of business data, and real-time aggregation of business data, use DM as the middleware for data migration

This document introduces how to use DM in an elegant and efficient way, and how to avoid common mistakes when using DM.
## Performance limitations

| Performance item  | Limitation |
| ----------------- | :--------: |
|  Max work nodes              |  1000           |
|  Max task number             |  600            |
|  Max QPS                     |  30k QPS/worker |
|  Max Binlog throughput       |  20 MB/s/worker |
|  Table number limit per task |  Unlimited      |

- DM supports managing 1000 work nodes simultaneously, and the maximum number of tasks is 600. To ensure the high availability of work nodes, you should reserve some work nodes as standby nodes. The recommended number of standby nodes is 20% to 50% of the number of the work nodes that have running migration tasks.
- A single work node can theoretically support replication QPS of up to 30K QPS/worker. It varies for different schemas and workloads. The ability to handle upstream binlogs is up to 20 MB/s/worker.
- If you want to use DM as a data replication middleware for long-term use, you need to carefully design the deployment architecture of DM components. For more information, see [Deploy DM-master and DM-worker](#deploy-dm-master-and-dm-worker)
## Before data migration

Before data migration, the design of the overall solution is critical. The following sections describe best practices and scenarios from the business perspective and the implementation perspective.
### Best practices for the business side

To distribute the workload evenly on multiple nodes, the design for the distributed database is different from traditional databases. The solution needs to ensure both low migration cost and logic correctness after migration. The following sections describe best practices before data migration.
#### Business impact of AUTO_INCREMENT in schema design

`AUTO_INCREMENT` in TiDB is compatible with `AUTO_INCREMENT` in MySQL. However, as a distributed database, TiDB usually has multiple computing nodes (entries for the client end). When the application data is written, the workload is evenly distributed. This leads to the result that when there is an `AUTO_INCREMENT` column in the table, the auto-increment IDs of the column might be inconsecutive. For more details, see [AUTO_INCREMENT](https://docs.pingcap.com/tidb/stable/auto-increment#implementation-principles).

If your business has a strong dependence on auto-increment IDs, consider using the [MySQL-compatible `AUTO_INCREMENT` mode](https://docs.pingcap.com/tidb/stable/auto-increment#mysql-compatibility-mode) or the [`SEQUENCE` function](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-sequence#sequence-function).
#### Usage of clustered indexes

When you create a table, you can declare that the primary key is either a clustered index or a non-clustered index. The following sections describe the pros and cons of each choice.

- Clustered indexes

    [Clustered indexes](https://docs.pingcap.com/tidb/stable/clustered-indexes) use the primary key as the handle ID (row ID) for data storage. Querying using the primary key can avoid table lookup, which effectively improves the query performance. However, if the table is write-intensive and the primary key uses [`AUTO_INCREMENT`](https://docs.pingcap.com/tidb/stable/auto-increment), it is very likely to cause [write hotspot problems](https://docs.pingcap.com/tidb/stable/best-practices/high-concurrency-best-practices#highly-concurrent-write-intensive-scenario), resulting in a mediocre performance of the cluster and the performance bottleneck of a single storage node.

- Non-clustered indexes + `shard row id bit`

    Using non-clustered indexes and `shard row id bit`, you can avoid the write hotspot problem when using `AUTO_INCREMENT`. However, table lookup in this scenario can affect the query performance when querying using the primary key.

- Clustered indexes + external distributed ID generators

    If you want to use clustered indexes and keep the IDs consecutive, consider using external distributed ID generators, such as the Snowflake algorithm and Leaf. The application program generates sequence IDs, which can guarantee that the IDs are consecutive to a certain extent. It also retains the benefits of using clustered indexes. But you need to customize the applications.

- Clustered indexes + `AUTO_RANDOM`

    This solution can retain the benefits of using clustered indexes and avoid the write hotspot problem. It requires less effort for customization. You can modify the schema attribute when you switch to use TiDB as the write database. In subsequent queries, if you have to use the ID column to sort data, you can use the [`AUTO_RANDOM`](https://docs.pingcap.com/tidb/stable/auto-random) ID column and left shift 6 bits (1 sign bit + 5 shard bits) to ensure the order of the query data. For example:

    ```sql
    CREATE TABLE t (a bigint PRIMARY KEY AUTO_RANDOM, b varchar(255));
    Select a, a<<6 ,b from t order by a <<6 desc
    ```

The following table summarizes the pros and cons of each solution.

| Scenario | Recommended solution | Pros | Cons |
| :--- | :--- | :--- | :--- |
| <li>TiDB will act as the primary and write-intensive database. </li><li>The business logic strongly relies on the continuity of the primary key IDs.</li> | Create tables with non-clustered indexes and set `SHARD_ROW_ID_BIT`. Use `SEQUENCE` as the primary key column.  | It can avoid data write hotspots and ensure the continuity and monotonic increment of business data. | <li>The throughput capacity of data write is decreased to ensure data write continuity. </li><li>The performance of primary key queries is decreased.</li> |
| <li>TiDB will act as the primary and write-intensive database. </li><li>The business logic strongly relies on the increment of the primary key IDs.</li>  | Create tables with non-clustered indexes and set `SHARD_ROW_ID_BIT`. Use an application ID generator to generate the primary key IDs. | It can avoid data write hotspots, guarantee the performance of data write, and guarantee the increment of business data, but cannot guarantee continuity. | <li>You need to customize the application. </li><li>External ID generators strongly rely on the clock accuracy and might introduce failures.</li> |
| <li>TiDB will act as the primary and write-intensive database. </li><li>The business logic does not rely on the continuity of the primary key IDs.</li> | Create tables with clustered indexes and set `AUTO_RANDOM` for the primary key column. | <li>It can avoid data write hotspots and has excellent query performance of primary keys. </li><li>You can smoothly switch from `AUTO_INCREMENT` to `AUTO_RANDOM`.</li> | <li>The primary key IDs are random. </li><li>The write throughput ability is limited. </li><li>It is recommended to sort the business data by using the insert time column. </li><li>If you have to use the primary key ID to sort data, you can left shift 5 bits to query, which can guarantee the increment of the data.</li> |
| TiDB will act as a read-only database. | Create tables with non-clustered indexes and set `SHARD_ROW_ID_BIT`. Keep the primary key column consistent with the data source. | <li>It can avoid data write hotspots. </li><li>It requires less customization cost. </li>| The query performance of primary keys is impacted. |
