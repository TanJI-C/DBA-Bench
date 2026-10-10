# Pre-splitting and scattering Regions to avoid write hotspots

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/best-practices/high-concurrency-best-practices.md`
- Source Title: `Highly Concurrent Write Best Practices`
- Source Heading Path: `Highly Concurrent Write Best Practices > Hotspot solution`
- Source Line Ranges: `132-203`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `pd`, `sql`
- Topic Tags: `split-region`, `pre-split`, `scatter-region`, `hotspot-mitigation`, `leader-distribution`, `show-table-regions`, `information-schema`, `write-scaling`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0059_925de686b4`
- Source ID: `tidb-docs-8.1:best-practices/high-concurrency-best-practices.md#hotspot-solution`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6ae2cdfbd79c1712db3b3fae57a7c4a2d9e975dbec40aab7fb2a413affb13a9c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/best-practices/high-concurrency-best-practices#hotspot-solution
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/best-practices/high-concurrency-best-practices.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB pre-splitting and scattering approach to avoid initial write hotspots in highly-concurrent write-heavy scenarios.
- Retrieval Keywords: Hotspot solution, Split Region, SPLIT TABLE table_name [INDEX index_name] BETWEEN (lower_value) AND (upper_value) REGIONS region_num, SPLIT TABLE table_name [INDEX index_name] BY (value_list), SPLIT TABLE TEST_HOTSPOT BETWEEN (0) AND (9223372036854775807) REGIONS 128, SHOW TABLE test_hotspot REGIONS, SCATTERING column, INFORMATION_SCHEMA.TIKV_REGION_STATUS, INFORMATION_SCHEMA.TIKV_REGION_PEERS, p.is_leader = 1, Region leader distribution, pre-split the index Region
- Follow-up Guidance: The source says to check `SHOW TABLE test_hotspot REGIONS;` for `SCATTERING = 0` and to query `INFORMATION_SCHEMA.TIKV_REGION_STATUS` joined with `INFORMATION_SCHEMA.TIKV_REGION_PEERS` to view leader distribution.
- Classification Note: This chunk is classified as performance because it presents the `Split Region` feature and related SQL checks to improve load distribution and resolve apparent hotspot problems.

## Official Source Content

## Hotspot solution

To achieve the ideal performance expected in theory, you can skip the warm-up phase by directly splitting a Region into the desired number of Regions and scheduling these Regions in advance to other nodes in the cluster.

In v3.0.x, v2.1.13 and later versions, TiDB supports a new feature called [Split Region](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-split-region). This new feature provides the following new syntaxes:

```sql
SPLIT TABLE table_name [INDEX index_name] BETWEEN (lower_value) AND (upper_value) REGIONS region_num
```

```sql
SPLIT TABLE table_name [INDEX index_name] BY (value_list) [, (value_list)]
```

However, TiDB does not automatically perform this pre-split operation. The reason is related to the data distribution in TiDB.

![Table Region Range](/media/best-practices/table-Region-range.png)

From the diagram above, according to the encoding rule of a row's key, the `rowID` is the only variable part. In TiDB, `rowID` is an `Int64` integer. However, you might not need to evenly split the `Int64` integer range to the desired number of ranges and then to distribute these ranges to different nodes, because Region split must also be based on the actual situation.

If the write of `rowID` is completely discrete, the above method will not cause hotspots. If the row ID or index has a fixed range or prefix (for example, discretely insert data into the range of `[2000w, 5000w)`), no hotspot will be caused either. However, if you split a Region using the above method, data might still be written to the same Region at the beginning.

TiDB is a database for general usage and does not make assumptions about the data distribution. So it uses only one Region at the beginning to store the data of a table and automatically splits the Region according to the data distribution after real data is inserted.

Given this situation and the need to avoid the hotspot problem, TiDB offers the `Split Region` syntax to optimize performance for the highly-concurrent write-heavy scenario. Based on the above case, now scatter Regions using the `Split Region` syntax and observe the load distribution.

Because the data to be written in the test is entirely discrete within the positive range, you can use the following statement to pre-split the table into 128 Regions within the range of `minInt64` and `maxInt64`:

```sql
SPLIT TABLE TEST_HOTSPOT BETWEEN (0) AND (9223372036854775807) REGIONS 128;
```

After the pre-split operation, execute the `SHOW TABLE test_hotspot REGIONS;` statement to check the status of Region scattering. If the values of the `SCATTERING` column are all `0`, the scheduling is successful.

You can also check the Region leader distribution using the following SQL statement. You need to replace `table_name` with the actual table name.

```sql
SELECT
    p.STORE_ID,
    COUNT(s.REGION_ID) PEER_COUNT
FROM
    INFORMATION_SCHEMA.TIKV_REGION_STATUS s
    JOIN INFORMATION_SCHEMA.TIKV_REGION_PEERS p ON s.REGION_ID = p.REGION_ID
WHERE
    TABLE_NAME = 'table_name'
    AND p.is_leader = 1
GROUP BY
    p.STORE_ID
ORDER BY
    PEER_COUNT DESC;
```

Then operate the write load again:

![QPS6](/media/best-practices/QPS6.png)

![QPS7](/media/best-practices/QPS7.png)

![QPS8](/media/best-practices/QPS8.png)

You can see that the apparent hotspot problem has been resolved now.

In this case, the table is simple. In other cases, you might also need to consider the hotspot problem of index. For more details on how to pre-split the index Region, refer to [Split Region](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-split-region).
