# PRE_SPLIT_REGIONS behavior and examples

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-split-region.md`
- Source Title: `Split Region`
- Source Heading Path: `Split Region > pre_split_regions | Split Region > pre_split_regions > Examples of pre_split_regions`
- Source Line Ranges: `355-389`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `pd`, `sql`
- Topic Tags: `pre-split-regions`, `auto-random`, `shard-row-id-bits`, `tidb-scatter-region`, `region-merge`, `write-performance`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0149_62fd0fef1b`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-split-region.md#pre-split-regions`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ac95de017d6bdddd63ec38c36c6869bfff9a96aabb817f2ad7309794ab1c9f37`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-split-region#pre-split-regions
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-split-region.md

## Retrieval Guidance

- Use When: Use this chunk when you need the behavior, limits, and examples of PRE_SPLIT_REGIONS for tables created with AUTO_RANDOM or SHARD_ROW_ID_BITS, including how tidb_scatter_region affects waiting for split and scatter completion.
- Retrieval Keywords: PRE_SPLIT_REGIONS, AUTO_RANDOM, SHARD_ROW_ID_BITS, tidb_scatter_region, CREATE TABLE t (a INT, b INT, INDEX idx1(a)) SHARD_ROW_ID_BITS = 4 PRE_SPLIT_REGIONS=2, 2^(PRE_SPLIT_REGIONS), PRE_SPLIT_REGIONS must be less than or equal to SHARD_ROW_ID_BITS or AUTO_RANDOM, pre-split Regions, split and scattered before returning results, write performance, Region merge, PD scheduler
- Follow-up Guidance: The chunk additionally notes that Regions split by the Split Region statement are controlled by the PD Region merge scheduler and references table attributes and dynamically modifying configuration items related to Region merge.
- Classification Note: This is classified as configuration because the content explains the PRE_SPLIT_REGIONS table option and the tidb_scatter_region global variable that affect Region pre-splitting behavior.

## Official Source Content

## pre_split_regions

When creating a table with the `AUTO_RANDOM` or `SHARD_ROW_ID_BITS` attribute, you can also specify the `PRE_SPLIT_REGIONS` option if you want to evenly pre-split the table into Regions immediately after the table is created. The number of pre-split Regions for a table is `2^(PRE_SPLIT_REGIONS)`.

> **Note:**
>
> The value of `PRE_SPLIT_REGIONS` must be less than or equal to that of `SHARD_ROW_ID_BITS` or `AUTO_RANDOM`.

The `tidb_scatter_region` global variable affects the behavior of `PRE_SPLIT_REGIONS`. This variable controls whether to wait for Regions to be pre-split and scattered before returning results after the table creation. If there are intensive writes after creating the table, you need to set the value of this variable to `1`, then TiDB will not return the results to the client until all the Regions are split and scattered. Otherwise, TiDB writes the data before the scattering is completed, which will have a significant impact on write performance.
### Examples of pre_split_regions

```sql
CREATE TABLE t (a INT, b INT, INDEX idx1(a)) SHARD_ROW_ID_BITS = 4 PRE_SPLIT_REGIONS=2;
```

After building the table, this statement splits `4 + 1` Regions for table t. `4 (2^2)` Regions are used to save table row data, and 1 Region is for saving the index data of `idx1`.

The ranges of the 4 table Regions are as follows:

```
region1:   [ -inf      ,  1<<61 )
region2:   [ 1<<61     ,  2<<61 )
region3:   [ 2<<61     ,  3<<61 )
region4:   [ 3<<61     ,  +inf  )
```

> **Note:**
>
> The Region split by the Split Region statement is controlled by the [Region merge](https://docs.pingcap.com/tidb/stable/best-practices/pd-scheduling-best-practices#region-merge) scheduler in PD. To avoid PD re-merging the newly split Region soon after, you need to use [table attributes](https://docs.pingcap.com/tidb/stable/table-attributes) or [dynamically modify](https://docs.pingcap.com/tidb/stable/pd-control) configuration items related to the Region merge feature.
