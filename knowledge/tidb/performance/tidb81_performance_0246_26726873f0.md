# _tidb_rowid hotspot mitigation and related references

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-rowid.md`
- Source Title: `_tidb_rowid`
- Source Heading Path: ``_tidb_rowid` > Address hotspot issues | `_tidb_rowid` > Related statements and variables | `_tidb_rowid` > See also`
- Source Line Ranges: `129-157`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `tikv`
- Topic Tags: `hotspot`, `row-id-allocation`, `shard-row-id-bits`, `pre-split-regions`, `next-row-id`, `clustered-indexes`, `references`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0246_26726873f0`
- Source ID: `tidb-docs-8.1:tidb-rowid.md#address-hotspot-issues`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5ac7a39107c91bae047b1790921c59439c58df2be0e239c8ebb0a74e01da7ee8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-rowid#address-hotspot-issues
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-rowid.md

## Retrieval Guidance

- Use When: Use this chunk when investigating write hotspot behavior caused by increasing `_tidb_rowid` allocation and looking for the related TiDB statements or options named in the documentation.
- Retrieval Keywords: Address hotspot issues, write hotspots, _tidb_rowid allocation in increasing order, write-intensive workloads, SHARD_ROW_ID_BITS, PRE_SPLIT_REGIONS, CREATE TABLE ... SHARD_ROW_ID_BITS = 4, SHOW TABLE NEXT_ROW_ID, Clustered Indexes, tidb_opt_write_row_id, shards implicit row IDs to reduce hotspots, pre-split Regions, does not apply to tables with clustered indexes
- Follow-up Guidance: The source also lists related references for `SHOW TABLE NEXT_ROW_ID`, `SHARD_ROW_ID_BITS`, `Clustered Indexes`, `tidb_opt_write_row_id`, `CREATE TABLE`, `AUTO_INCREMENT`, and Non-transactional DML.
- Classification Note: This is classified as performance content because it discusses hotspot mitigation for increasing `_tidb_rowid` allocation and names the related row ID sharding and Region pre-splitting features.

## Official Source Content

## Address hotspot issues

For tables that use `_tidb_rowid`, TiDB allocates row IDs in increasing order by default. In write-intensive workloads, this can create write hotspots.

To mitigate this issue (for tables that rely on `_tidb_rowid` as the row ID), consider using [`SHARD_ROW_ID_BITS`](https://docs.pingcap.com/tidb/stable/shard-row-id-bits) to distribute row IDs more evenly, and use [`PRE_SPLIT_REGIONS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-split-region#pre_split_regions) to pre-split Regions when necessary.

Example:

```sql
CREATE TABLE t (
    id BIGINT PRIMARY KEY NONCLUSTERED,
    c INT
) SHARD_ROW_ID_BITS = 4;
```

`SHARD_ROW_ID_BITS` applies only to tables that use `_tidb_rowid` and does not apply to tables with clustered indexes.
## Related statements and variables

- [`SHOW TABLE NEXT_ROW_ID`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-table-next-rowid): shows the next row ID that TiDB will allocate
- [`SHARD_ROW_ID_BITS`](https://docs.pingcap.com/tidb/stable/shard-row-id-bits): shards implicit row IDs to reduce hotspots
- [`Clustered Indexes`](https://docs.pingcap.com/tidb/stable/clustered-indexes): explains when a table uses the primary key instead of `_tidb_rowid`
- [`tidb_opt_write_row_id`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_write_row_id): controls whether writes to `_tidb_rowid` are allowed
## See also

- [`CREATE TABLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-table)
- [`AUTO_INCREMENT`](https://docs.pingcap.com/tidb/stable/auto-increment)
- [Non-transactional DML](https://docs.pingcap.com/tidb/stable/non-transactional-dml)
