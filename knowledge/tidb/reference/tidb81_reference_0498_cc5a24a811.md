# SHARD_ROW_ID_BITS concept and SQL examples

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/shard-row-id-bits.md`
- Source Title: `SHARD_ROW_ID_BITS`
- Source Heading Path: `SHARD_ROW_ID_BITS | SHARD_ROW_ID_BITS > Concept | SHARD_ROW_ID_BITS > Examples`
- Source Line Ranges: `5-62`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `sql`
- Topic Tags: `shard_row_id_bits`, `_tidb_rowid`, `implicit-rowid`, `hotspot-mitigation`, `region-distribution`, `auto-increment-bits`, `table-attribute`, `create-table`, `alter-table`, `partition-warning`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0498_cc5a24a811`
- Source ID: `tidb-docs-8.1:shard-row-id-bits.md#shard-row-id-bits`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7abbe8cf6fc9d4cafc94e86e90d3dc6ffed5a791e1ff3bcb401f446823048846`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/shard-row-id-bits#shard-row-id-bits
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/shard-row-id-bits.md

## Retrieval Guidance

- Use When: Use this chunk when explaining what `SHARD_ROW_ID_BITS` does for tables that use implicit `_tidb_rowid`, how it mitigates `INSERT` write hot spot issues by scattering row IDs across Regions, or what SQL syntax sets it.
- Retrieval Keywords: SHARD_ROW_ID_BITS, _tidb_rowid, implicit auto-increment row ID, write hot spot, single Region, multiple different Regions, SHARD_ROW_ID_BITS = 4, 16 shards, SHARD_ROW_ID_BITS = 6, 64 shards, SHARD_ROW_ID_BITS = 0, 1 shard, sign bit, shard bits, auto-increment bits, Failed to read auto-increment value from storage engine, (2^63)-1, ALTER TABLE ... EXCHANGE PARTITION, partitioned tables, non-clustered primary key, CREATE TABLE t ( id INT PRIMARY KEY NONCLUSTERED ) SHARD_ROW_ID_BITS = 4, ALTER TABLE t SHARD_ROW_ID_BITS = 4, log(2, x), TiKV nodes, Troubleshoot Hotspot Issues
- Follow-up Guidance: The content also points to the Troubleshoot Hotspot Issues guide for more usage details and warns that `_tidb_rowid` is not guaranteed to be globally unique in all cases, especially with `ALTER TABLE ... EXCHANGE PARTITION` on partitioned tables without clustered indexes.
- Classification Note: This is reference content because it defines the `SHARD_ROW_ID_BITS` table attribute, describes its `_tidb_rowid` bit layout and limits, includes warnings and error text, and shows exact `CREATE TABLE` and `ALTER TABLE` examples.

## Official Source Content

# SHARD_ROW_ID_BITS

This document introduces the `SHARD_ROW_ID_BITS` table attribute, which is used to set the number of bits of the shards after the implicit [`_tidb_rowid`](https://docs.pingcap.com/tidb/stable/tidb-rowid) is sharded.
## Concept

For tables with a non-clustered primary key or no primary key, TiDB uses the automatically generated [`_tidb_rowid`](https://docs.pingcap.com/tidb/stable/tidb-rowid) as an implicit auto-increment row ID. When a large number of `INSERT` operations are performed, the data is written into a single Region, causing a write hot spot.

To mitigate the hot spot issue, you can configure `SHARD_ROW_ID_BITS`. The row IDs are scattered and the data are written into multiple different Regions.

- `SHARD_ROW_ID_BITS = 4` indicates 16 shards
- `SHARD_ROW_ID_BITS = 6` indicates 64 shards
- `SHARD_ROW_ID_BITS = 0` indicates the default 1 shard

When you set `SHARD_ROW_ID_BITS = S`, the structure of `_tidb_rowid` is as follows:

| Sign bit |  Shard bits | Auto-increment bits |
|--------|--------|--------------|
| 1 bit | `S` bits | `63-S` bits |

- The values of the auto-increment bits are stored in TiKV and allocated sequentially. Each time a value is allocated, the next value is incremented by 1. When the value of the auto-increment bits is exhausted (that is, when the maximum value is reached), subsequent automatic allocations fail with the error `Failed to read auto-increment value from storage engine`.
- The value range of `_tidb_rowid`: the maximum number of bits for the final generated value = shard bits + auto-increment bits, so the maximum value is `(2^63)-1`.

> **Warning:**
>
> `_tidb_rowid` is an internal row ID implicitly assigned by TiDB. Do not assume it is globally unique in all cases. For partitioned tables that do not use clustered indexes, `ALTER TABLE ... EXCHANGE PARTITION` can leave different partitions with the same `_tidb_rowid` value. For details, see [`_tidb_rowid`](https://docs.pingcap.com/tidb/stable/tidb-rowid).

> **Note:**
>
> Selection of shard bits (`S`):
>
> - Because the total bits of `_tidb_rowid` is 64, the number of shard bits affects the number of auto-increment bits: when the number of shard bits increases, the number of auto-increment bits decreases, and vice versa. Therefore, you need to balance the randomness of the auto-increment values and the available auto-increment space.
> - The best practice is to set the shard bits to `log(2, x)`, where `x` is the number of TiKV nodes in the cluster. For example, if there are 16 TiKV nodes in a TiDB cluster, it is recommended to set the shard bits to `log(2, 16)`, which equals `4`. After all Regions are evenly scheduled to each TiKV node, the load of bulk writes can be evenly distributed to different TiKV nodes to maximize resource utilization.

For details on the usage, see [the Troubleshoot Hotspot Issues guide](https://docs.pingcap.com/tidb/stable/troubleshoot-hot-spot-issues#use-shard_row_id_bits-to-process-hotspots).

For details on the usage, see [the Troubleshoot Hotspot Issues guide](https://docs.pingcap.com/tidb/stable/troubleshoot-hot-spot-issues#use-shard_row_id_bits-to-process-hotspots).
## Examples

```sql
CREATE TABLE t (
    id INT PRIMARY KEY NONCLUSTERED
) SHARD_ROW_ID_BITS = 4;
```

```sql
ALTER TABLE t SHARD_ROW_ID_BITS = 4;
```
