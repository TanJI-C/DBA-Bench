# HTAP quick start setup, TiFlash replication, and first query

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tidb-cloud-htap-quickstart.md`
- Source Title: `TiDB Cloud HTAP Quick Start`
- Source Heading Path: `TiDB Cloud HTAP Quick Start | TiDB Cloud HTAP Quick Start > Before you begin | TiDB Cloud HTAP Quick Start > Steps | TiDB Cloud HTAP Quick Start > Steps > Step 1. Replicate the sample data to the columnar storage engine | TiDB Cloud HTAP Quick Start > Steps > Step 2. Query data using HTAP`
- Source Line Ranges: `6-72`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`, `tiflash`, `tikv`, `sql`
- Topic Tags: `htap`, `quickstart`, `prerequisites`, `replication`, `tiflash-replica`, `ddl`, `sample-data`, `query`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0417_ac17f2f3d1`
- Source ID: `tidb-docs-8.1:tidb-cloud/tidb-cloud-htap-quickstart.md#tidb-cloud-htap-quick-start`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `319f18cdd8acf24ddcac63516257b79f73773d0e86472d199fc8723f07f21721`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-htap-quickstart#tidb-cloud-htap-quick-start
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tidb-cloud-htap-quickstart.md

## Retrieval Guidance

- Use When: Use this chunk when the user wants the TiDB Cloud HTAP quick start steps for enabling TiFlash replication on the Steam Game Stats sample dataset and running a first HTAP query.
- Retrieval Keywords: TiDB Cloud HTAP Quick Start, Steam Game Stats, TiDB Cloud Serverless cluster, TiFlash replica, ALTER TABLE games SET TIFLASH REPLICA 2, information_schema.tiflash_replica, AVAILABLE, PROGRESS, USE game, games table, Query data using HTAP
- Follow-up Guidance: It also shows how to check replication progress with SELECT TABLE_SCHEMA, TABLE_NAME, TABLE_ID, REPLICA_COUNT, LOCATION_LABELS, AVAILABLE, PROGRESS FROM information_schema.tiflash_replica WHERE TABLE_SCHEMA = 'game' and TABLE_NAME = 'games'.
- Classification Note: This is classified as an operation chunk because the content provides prerequisite context plus concrete setup and query steps for TiFlash replication and HTAP querying in TiDB Cloud.

## Official Source Content

# TiDB Cloud HTAP Quick Start

[HTAP](https://en.wikipedia.org/wiki/Hybrid_transactional/analytical_processing) means Hybrid Transactional and Analytical Processing. The HTAP cluster in TiDB Cloud is composed of [TiKV](https://tikv.org), a row-based storage engine designed for transactional processing, and [TiFlash](https://docs.pingcap.com/tidb/stable/tiflash-overview), a columnar storage designed for analytical processing. Your application data is first stored in TiKV and then replicated to TiFlash via the Raft consensus algorithm. So it is a real-time replication from the row-based storage to the columnar storage.

This tutorial guides you through an easy way to experience the Hybrid Transactional and Analytical Processing (HTAP) feature of TiDB Cloud. The content includes how to replicate tables to TiFlash, how to run queries with TiFlash, and how to experience the performance boost.
## Before you begin

Before experiencing the HTAP feature, follow [TiDB Cloud Quick Start](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-quickstart) to create a TiDB Cloud Serverless cluster and import the **Steam Game Stats** sample dataset to the cluster.
## Steps
### Step 1. Replicate the sample data to the columnar storage engine

After a cluster with TiFlash nodes is created, TiKV does not replicate data to TiFlash by default. You need to execute DDL statements in a MySQL client of TiDB to specify the tables to be replicated. After that, TiDB will create the specified table replicas in TiFlash accordingly.

For example, to replicate the `games` table (in the **Steam Game Stats** sample dataset) to TiFlash, execute the following statements:

```sql
USE game;
```

```sql
ALTER TABLE games SET TIFLASH REPLICA 2;
```

To check the replication progress, execute the following statement:

```sql
SELECT TABLE_SCHEMA, TABLE_NAME, TABLE_ID, REPLICA_COUNT, LOCATION_LABELS, AVAILABLE, PROGRESS FROM information_schema.tiflash_replica WHERE TABLE_SCHEMA = 'game' and TABLE_NAME = 'games';
```

```sql
+--------------+------------+----------+---------------+-----------------+-----------+----------+
| TABLE_SCHEMA | TABLE_NAME | TABLE_ID | REPLICA_COUNT | LOCATION_LABELS | AVAILABLE | PROGRESS |
+--------------+------------+----------+---------------+-----------------+-----------+----------+
| game         | games      |       88 |             2 |                 |         1 |        1 |
+--------------+------------+----------+---------------+-----------------+-----------+----------+
1 row in set (0.20 sec)
```

In the result of the preceding statement:

- `AVAILABLE` indicates whether the TiFlash replica of a specific table is available or not. `1` means available and `0` means unavailable. Once a replica becomes available, this status does not change anymore.
- `PROGRESS` means the progress of the replication. The value is between `0` and `1`. `1` means at least one replica is replicated.
### Step 2. Query data using HTAP

When the process of replication is completed, you can start to run some queries.

For example, you can check the number of games released every year, as well as the average price and average playtime:

```sql
SELECT
  YEAR(`release_date`) AS `release_year`,
  COUNT(*) AS `games_released`,
  AVG(`price`) AS `average_price`,
  AVG(`average_playtime_forever`) AS `average_playtime`
FROM
  `games`
GROUP BY
  `release_year`
ORDER BY
  `release_year` DESC;
```
