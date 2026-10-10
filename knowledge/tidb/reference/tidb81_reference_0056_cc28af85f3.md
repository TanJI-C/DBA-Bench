# Clustered index limitations and unsupported scenarios

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/clustered-indexes.md`
- Source Title: `Clustered Indexes`
- Source Heading Path: `Clustered Indexes > Limitations`
- Source Line Ranges: `141-166`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `shared`, `ticdc`
- Topic Tags: `limitations`, `unsupported-scenarios`, `downgrade`, `binlog`, `alter-table`, `shard-row-id-bits`, `pre-split-regions`, `auto-random`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0056_cc28af85f3`
- Source ID: `tidb-docs-8.1:clustered-indexes.md#limitations`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `894870d038834c7e4efd878a1311381ed8904ed6385d3ce73c0f04d158dc6fa1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/clustered-indexes#limitations
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/clustered-indexes.md

## Retrieval Guidance

- Use When: Use this chunk when looking for unsupported scenarios, errors, or version-specific limitations of clustered indexes involving SHARD_ROW_ID_BITS, PRE_SPLIT_REGIONS, ALTER TABLE, downgrade, or TiDB Binlog.
- Retrieval Keywords: Clustered Indexes Limitations, SHARD_ROW_ID_BITS, PRE_SPLIT_REGIONS, AUTO_RANDOM, ALTER TABLE, downgrading tables with clustered indexes is not supported, logical backup tools to migrate data, TiDB Binlog, Cannot create clustered index table when the binlog is ON, Unsupported shard_row_id_bits for table with primary key as row id, single integer primary key, TiCDC
- Follow-up Guidance: The content also states that in v5.0 TiDB Binlog does not replicate data changes on existing tables with clustered indexes to the downstream, and mentions upgrading to v5.1 or using TiCDC for replication instead.
- Classification Note: This is reference content because it enumerates official limitations, unsupported scenarios, and exact error messages for clustered indexes.

## Official Source Content

## Limitations

Currently, there are several different types of limitations for the clustered index feature. See the following:

- Situations that are not supported and not in the support plan:
    - Using clustered indexes together with the attribute [`SHARD_ROW_ID_BITS`](https://docs.pingcap.com/tidb/stable/shard-row-id-bits) is not supported. Also, the attribute [`PRE_SPLIT_REGIONS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-split-region#pre_split_regions) does not take effect on tables with clustered indexes that are not [`AUTO_RANDOM`](https://docs.pingcap.com/tidb/stable/auto-random).
    - Downgrading tables with clustered indexes is not supported. If you need to downgrade such tables, use logical backup tools to migrate data instead.
- Situations that are not supported yet but in the support plan:
    - Adding, dropping, and altering clustered indexes using `ALTER TABLE` statements are not supported.
- Limitations for specific versions:    
    - In v5.0, using the clustered index feature together with TiDB Binlog is not supported. After TiDB Binlog is enabled, TiDB only allows creating a single integer column as the clustered index of a primary key. TiDB Binlog does not replicate data changes (such as insertion, deletion, and update) on existing tables with clustered indexes to the downstream. If you need to replicate tables with clustered indexes to the downstream, upgrade your cluster to v5.1 or use [TiCDC](https://docs.pingcap.com/tidb/stable/ticdc-overview) for replication instead.

After TiDB Binlog is enabled, if the clustered index you create is not a single integer primary key, TiDB returns the following error:

```sql
mysql> CREATE TABLE t (a VARCHAR(255) PRIMARY KEY CLUSTERED);
ERROR 8200 (HY000): Cannot create clustered index table when the binlog is ON
```

If you use clustered indexes together with the attribute `SHARD_ROW_ID_BITS`, TiDB reports the following error:

```sql
mysql> CREATE TABLE t (a VARCHAR(255) PRIMARY KEY CLUSTERED) SHARD_ROW_ID_BITS = 3;
ERROR 8200 (HY000): Unsupported shard_row_id_bits for table with primary key as row id
```
