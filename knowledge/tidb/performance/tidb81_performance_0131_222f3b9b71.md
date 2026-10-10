# Partition pruning basics

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/partitioned-table.md`
- Source Title: `Partitioning`
- Source Heading Path: `Partitioning > Partition pruning`
- Source Line Ranges: `1204-1246`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `partition-pruning`, `optimizer`, `where-clause`, `query-performance`, `range-partition`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0131_222f3b9b71`
- Source ID: `tidb-docs-8.1:partitioned-table.md#partition-pruning`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e0e99b40e42bdce899c5ff41c8998e9cc261597f7efac947eceb797d6e517fec`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/partitioned-table#partition-pruning
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/partitioned-table.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the basic meaning of partition pruning, when it improves query performance, and which WHERE conditions allow the optimizer to prune partitions.
- Retrieval Keywords: Partition pruning, optimizer, do not scan the partitions that do not match, WHERE region_code > 125 AND region_code < 130, partition_column = constant, partition_column IN (constant1, constant2, ..., constantN), LIKE conditions, partition pruning does not work with LIKE conditions, range partition, query performance
- Follow-up Guidance: The source says the optimizer can prune partitions through WHERE conditions for partition_column = constant and partition_column IN (...), but currently not with LIKE conditions.
- Classification Note: This is classified as a performance chunk because it explains an optimizer behavior that can make queries on partitioned tables faster.

## Official Source Content

## Partition pruning

[Partition pruning](https://docs.pingcap.com/tidb/stable/partition-pruning) is an optimization which is based on a very simple idea - do not scan the partitions that do not match.

Assume that you create a partitioned table `t1`:

```sql
CREATE TABLE t1 (
    fname VARCHAR(50) NOT NULL,
    lname VARCHAR(50) NOT NULL,
    region_code TINYINT UNSIGNED NOT NULL,
    dob DATE NOT NULL
)

PARTITION BY RANGE( region_code ) (
    PARTITION p0 VALUES LESS THAN (64),
    PARTITION p1 VALUES LESS THAN (128),
    PARTITION p2 VALUES LESS THAN (192),
    PARTITION p3 VALUES LESS THAN MAXVALUE
);
```

If you want to get the result of this `SELECT` statement:

```sql
SELECT fname, lname, region_code, dob
    FROM t1
    WHERE region_code > 125 AND region_code < 130;
```

It is evident that the result falls in either the `p1` or the `p2` partition, that is, you just need to search for the matching rows in `p1` and `p2`. Excluding the unneeded partitions is so-called "pruning". If the optimizer is able to prune a part of partitions, the execution of the query in the partitioned table will be much faster than that in a non-partitioned table.

The optimizer can prune partitions through `WHERE` conditions in the following two scenarios:

* partition_column = constant
* partition_column IN (constant1, constant2, ..., constantN)

Currently, partition pruning does not work with `LIKE` conditions.
