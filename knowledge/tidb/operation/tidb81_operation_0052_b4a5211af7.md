# Enable TiFlash replication for HTAP table analysis

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-create-table.md`
- Source Title: `Create a Table`
- Source Heading Path: `Create a Table > Use HTAP capabilities | Create a Table > Use HTAP capabilities > Replicate column-based data | Create a Table > Use HTAP capabilities > An example of using HTAP capabilities`
- Source Line Ranges: `232-310`
- Source Scope: `all`
- Primary Component: `tiflash`
- Related Components: `tidb`, `tikv`, `cloud`, `sql`
- Topic Tags: `htap`, `tiflash`, `replica`, `olap`, `mpp`, `cost-based-selection`, `explain-analyze`, `alter-table`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0052_b4a5211af7`
- Source ID: `tidb-docs-8.1:develop/dev-guide-create-table.md#use-htap-capabilities`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4effe6ed7cea06612087640bfdde5d5385799ca6a295b83d9dd60aad1956f20e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-create-table#use-htap-capabilities
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-create-table.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks how to enable TiFlash replicas for a table and verify HTAP query execution on TiFlash with ALTER TABLE and EXPLAIN ANALYZE.
- Retrieval Keywords: Use HTAP capabilities, TiFlash, HTAP, OLAP, OLTP, ALTER TABLE {table_name} SET TIFLASH REPLICA {count};, SET TIFLASH REPLICA 1, bookshop.ratings, EXPLAIN ANALYZE, SELECT HOUR(`rated_at`), AVG(`score`) FROM `bookshop`.`ratings` GROUP BY HOUR(`rated_at`), cost optimization, TiKV, TiFlash MPP, Use TiDB to read TiFlash replicas, 1105 - the tiflash replica count: 1 should be less than the total tiflash server count: 0
- Follow-up Guidance: The chunk includes a quick-start example that sets `bookshop`.`ratings` to `TIFLASH REPLICA 1`, runs an aggregate query, and checks TiFlash usage with `EXPLAIN ANALYZE`.
- Classification Note: This is operational content because it describes the procedure and related SQL for enabling TiFlash replication and observing HTAP query behavior.

## Official Source Content

## Use HTAP capabilities

> **Note:**
>
> The steps provided in this guide is **_ONLY_** for quick start in the test environment. For production environments, refer to [explore HTAP](https://docs.pingcap.com/tidb/stable/explore-htap).

> **Note:**
>
> The steps provided in this guide is **_ONLY_** for quick start. For more instructions, refer to [Use an HTAP Cluster with TiFlash](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-overview).

Suppose that you want to perform OLAP analysis on the `ratings` table using the `bookshop` application, for example, to query **whether the rating of a book has a significant correlation with the time of the rating**, which is to analyze whether the user's rating of the book is objective or not. Then you need to query the `score` and `rated_at` fields of the entire `ratings` table. This operation is resource-intensive for an OLTP-only database. Or you can use some ETL or other data synchronization tools to export the data from the OLTP database to a dedicated OLAP database for analysis.

In this scenario, TiDB, an **HTAP (Hybrid Transactional and Analytical Processing)** database that supports both OLTP and OLAP scenarios, is an ideal one-stop database solution.
### Replicate column-based data

Currently, TiDB supports two data analysis engines, **TiFlash** and **TiSpark**. For the large data scenarios (100 T), **TiFlash MPP** is recommended as the primary solution for HTAP, and **TiSpark** as a complementary solution.

To learn more about TiDB HTAP capabilities, refer to the following documents: [Quick Start Guide for TiDB HTAP](https://docs.pingcap.com/tidb/stable/quick-start-with-htap) and [Explore HTAP](https://docs.pingcap.com/tidb/stable/explore-htap).

To learn more about TiDB HTAP capabilities, see [TiDB Cloud HTAP Quick Start](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-htap-quickstart) and [Use an HTAP Cluster with TiFlash](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-overview).

In this example, [TiFlash](https://docs.pingcap.com/tidb/stable/tiflash-overview) has been chosen as the data analysis engine for the `bookshop` database.

TiFlash does not automatically replicate data after deployment. Therefore, you need to manually specify the tables to be replicated:

```sql
ALTER TABLE {table_name} SET TIFLASH REPLICA {count};
```

**Parameter description**

- `{table_name}`: The table name.
- `{count}`: The number of replicated replicas. If it is 0, replicated replicas are deleted.

**TiFlash** will then replicate the table. When a query is performed, TiDB automatically selects TiKV (row-based) or TiFlash (column-based) for the query based on cost optimization. Alternatively, you can manually specify whether the query uses a **TiFlash** replica. To learn how to specify it, refer to [Use TiDB to read TiFlash replicas](https://docs.pingcap.com/tidb/stable/tiflash/use-tidb-to-read-tiflash).
### An example of using HTAP capabilities

The `ratings` table opens `1` replica of TiFlash:

```sql
ALTER TABLE `bookshop`.`ratings` SET TIFLASH REPLICA 1;
```

> **Note:**
>
> If your cluster does not contain **TiFlash** nodes, this SQL statement will report an error: `1105 - the tiflash replica count: 1 should be less than the total tiflash server count: 0`. You can use [Build a {{{ .starter }}} Cluster](https://docs.pingcap.com/tidb/stable/develop/dev-guide-build-cluster-in-cloud#step-1-create-a-tidb-cloud-cluster) to create a {{{ .starter }}} cluster that includes **TiFlash**.

Then you can go on to perform the following query:

```sql
SELECT HOUR(`rated_at`), AVG(`score`) FROM `bookshop`.`ratings` GROUP BY HOUR(`rated_at`);
```

You can also execute the [`EXPLAIN ANALYZE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-explain-analyze) statement to see whether this statement is using the **TiFlash**:

```sql
EXPLAIN ANALYZE SELECT HOUR(`rated_at`), AVG(`score`) FROM `bookshop`.`ratings` GROUP BY HOUR(`rated_at`);
```

Running results:
