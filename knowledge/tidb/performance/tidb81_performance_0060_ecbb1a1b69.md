# Complex hotspot problems and row ID scattering options

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/best-practices/high-concurrency-best-practices.md`
- Source Title: `Highly Concurrent Write Best Practices`
- Source Heading Path: `Highly Concurrent Write Best Practices > Complex hotspot problems`
- Source Line Ranges: `204-242`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `shared`
- Topic Tags: `hotspot`, `rowid`, `shard_row_id_bits`, `pre_split_regions`, `auto_increment`, `auto_random`, `region-scattering`, `write-performance`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0060_ecbb1a1b69`
- Source ID: `tidb-docs-8.1:best-practices/high-concurrency-best-practices.md#complex-hotspot-problems`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0faa0418350632fa10374fbc3b4a284c45898ede0a3d9a759092bd388fe3dec8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/best-practices/high-concurrency-best-practices#complex-hotspot-problems
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/best-practices/high-concurrency-best-practices.md

## Retrieval Guidance

- Use When: Use this chunk when asking how TiDB handles complex write hotspots related to monotonically increasing `_tidb_rowid` or integer primary keys with `AUTO_INCREMENT`, and which table options scatter writes across Regions.
- Retrieval Keywords: _tidb_rowid, SHARD_ROW_ID_BITS, PRE_SPLIT_REGIONS, tidb_scatter_region, AUTO_INCREMENT, AUTO_RANDOM, create table t (a int, b int) SHARD_ROW_ID_BITS = 4 PRE_SPLIT_REGIONS=3, pre-split Regions, hotspot problem, row ID scattering, integer primary key
- Follow-up Guidance: The source also notes that `PRE_SPLIT_REGIONS` must be smaller than or equal to `SHARD_ROW_ID_BITS`, and that `tidb_scatter_region` affects whether TiDB waits for Regions to be split and scattered before returning after table creation.
- Classification Note: This is classified as performance content because it describes hotspot avoidance and write performance behavior using row ID scattering, pre-splitting Regions, and primary key generation options.

## Official Source Content

## Complex hotspot problems

**Problem one:**

If a table does not have a primary key, or the primary key is not the `Int` type and you do not want to generate a randomly distributed primary key ID, TiDB provides an implicit `_tidb_rowid` column as the row ID. Generally, when you do not use the `SHARD_ROW_ID_BITS` parameter, the values of the `_tidb_rowid` column are also monotonically increasing, which might causes hotspots too. Refer to [`SHARD_ROW_ID_BITS`](https://docs.pingcap.com/tidb/stable/shard-row-id-bits) for more details.

To avoid the hotspot problem in this situation, you can use `SHARD_ROW_ID_BITS` and `PRE_SPLIT_REGIONS` when creating a table. For more details about `PRE_SPLIT_REGIONS`, refer to [Pre-split Regions](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-split-region#pre_split_regions).

`SHARD_ROW_ID_BITS` is used to randomly scatter the row ID generated in the `_tidb_rowid` column. `PRE_SPLIT_REGIONS` is used to pre-split the Region after a table is created.

> **Note:**
>
> The value of `PRE_SPLIT_REGIONS` must be smaller than or equal to that of `SHARD_ROW_ID_BITS`.

Example:

```sql
create table t (a int, b int) SHARD_ROW_ID_BITS = 4 PRE_SPLIT_REGIONS=3;
```

- `SHARD_ROW_ID_BITS = 4` means that the values of `tidb_rowid` will be randomly distributed into 16 (16=2^4) ranges.
- `PRE_SPLIT_REGIONS=3` means that the table will be pre-split into 8 (2^3) Regions after it is created.

When data starts to be written into table `t`, the data is written into the pre-split 8 Regions, which avoids the hotspot problem that might be caused if only one Region exists after table creation.

> **Note:**
>
> The `tidb_scatter_region` global variable affects the behavior of `PRE_SPLIT_REGIONS`.
>
> This variable controls whether to wait for Regions to be pre-split and scattered before returning results after the table creation. If there are intensive writes after creating the table, you need to set the value of this variable to `1`, then TiDB will not return the results to the client until all the Regions are split and scattered. Otherwise, TiDB writes data before the scattering is completed, which will have a significant impact on write performance.

**Problem two:**

If a table's primary key is an integer type, and if the table uses `AUTO_INCREMENT` to ensure the uniqueness of the primary key (not necessarily continuous or incremental), you cannot use `SHARD_ROW_ID_BITS` to scatter the hotspot on this table because TiDB directly uses the row values of the primary key as `_tidb_rowid`.

To address the problem in this scenario, you can replace `AUTO_INCREMENT` with [`AUTO_RANDOM`](https://docs.pingcap.com/tidb/stable/auto-random) (a column attribute) when inserting data. Then TiDB automatically assigns values to the integer primary key column, which eliminates the continuity of the row ID and scatters the hotspot.
