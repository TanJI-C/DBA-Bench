# Use Runtime Filter with TiFlash replicas

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/runtime-filter.md`
- Source Title: `Runtime Filter`
- Source Heading Path: `Runtime Filter > Use Runtime Filter | Runtime Filter > Use Runtime Filter > Step 1. Create TiFlash replicas for tables to be joined | Runtime Filter > Use Runtime Filter > Step 2. Enable Runtime Filter`
- Source Line Ranges: `79-132`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tiflash`, `sql`
- Topic Tags: `runtime filter`, `tiflash replica`, `system variable`, `enablement`, `verification`, `mpp`, `join query`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0213_d2337056f0`
- Source ID: `tidb-docs-8.1:runtime-filter.md#use-runtime-filter`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8afb74117072400d69a4bcef3b4f825b4a4407f33e6c7a8a4258997c25448849`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/runtime-filter#use-runtime-filter
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/runtime-filter.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the documented setup steps to use Runtime Filter with joined tables that have TiFlash replicas and to verify the related system variable and replica status.
- Retrieval Keywords: Use Runtime Filter, TiFlash replicas, ALTER TABLE catalog_sales SET tiflash REPLICA 1, ALTER TABLE date_dim SET tiflash REPLICA 1, INFORMATION_SCHEMA.TIFLASH_REPLICA, AVAILABLE, PROGRESS, tidb_runtime_filter_mode, SET tidb_runtime_filter_mode="LOCAL", SHOW VARIABLES LIKE "tidb_runtime_filter_mode", LOCAL, catalog_sales, date_dim
- Follow-up Guidance: The official steps check that `AVAILABLE` and `PROGRESS` are both `1` in `INFORMATION_SCHEMA.TIFLASH_REPLICA` and that `SHOW VARIABLES LIKE "tidb_runtime_filter_mode"` returns `LOCAL`.
- Classification Note: This chunk is classified as operation because the official content provides procedural enablement and verification steps for Runtime Filter using TiFlash replicas and the `tidb_runtime_filter_mode` system variable.

## Official Source Content

## Use Runtime Filter

To use Runtime Filter, you need to create a table with TiFlash replicas and set [`tidb_runtime_filter_mode`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_runtime_filter_mode-new-in-v720) to `LOCAL`.

Taking the TPC-DS dataset as an example, this section uses the `catalog_sales` table and the `date_dim` table for join operations to illustrate how Runtime Filter improves query efficiency.
### Step 1. Create TiFlash replicas for tables to be joined

Add a TiFlash replica to each of the `catalog_sales` table and the `date_dim` table.

```sql
ALTER TABLE catalog_sales SET tiflash REPLICA 1;
ALTER TABLE date_dim SET tiflash REPLICA 1;
```

Wait until the TiFlash replicas of the two tables are ready, that is, the `AVAILABLE` and `PROGRESS` fields of the replicas are both `1`.

```sql
SELECT * FROM INFORMATION_SCHEMA.TIFLASH_REPLICA WHERE TABLE_NAME='catalog_sales';
+--------------+---------------+----------+---------------+-----------------+-----------+----------+
| TABLE_SCHEMA | TABLE_NAME    | TABLE_ID | REPLICA_COUNT | LOCATION_LABELS | AVAILABLE | PROGRESS |
+--------------+---------------+----------+---------------+-----------------+-----------+----------+
| tpcds50      | catalog_sales |     1055 |             1 |                 |         1 |        1 |
+--------------+---------------+----------+---------------+-----------------+-----------+----------+

SELECT * FROM INFORMATION_SCHEMA.TIFLASH_REPLICA WHERE TABLE_NAME='date_dim';
+--------------+------------+----------+---------------+-----------------+-----------+----------+
| TABLE_SCHEMA | TABLE_NAME | TABLE_ID | REPLICA_COUNT | LOCATION_LABELS | AVAILABLE | PROGRESS |
+--------------+------------+----------+---------------+-----------------+-----------+----------+
| tpcds50      | date_dim   |     1015 |             1 |                 |         1 |        1 |
+--------------+------------+----------+---------------+-----------------+-----------+----------+
```
### Step 2. Enable Runtime Filter

To enable Runtime Filter, set the value of the system variable [`tidb_runtime_filter_mode`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_runtime_filter_mode-new-in-v720  ) to `LOCAL`.

```sql
SET tidb_runtime_filter_mode="LOCAL";
```

Check whether the change is successful:

```sql
SHOW VARIABLES LIKE "tidb_runtime_filter_mode";
+--------------------------+-------+
| Variable_name            | Value |
+--------------------------+-------+
| tidb_runtime_filter_mode | LOCAL |
+--------------------------+-------+
```

If the value of the system variable is `LOCAL`, Runtime Filter is enabled.
