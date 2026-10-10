# TiFlash spill to disk triggers, examples, and notes

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiflash/tiflash-spill-disk.md`
- Source Title: `TiFlash Spill to Disk`
- Source Heading Path: `TiFlash Spill to Disk | TiFlash Spill to Disk > Trigger the spilling | TiFlash Spill to Disk > Trigger the spilling > Operator-level spilling | TiFlash Spill to Disk > Trigger the spilling > Operator-level spilling > Example | TiFlash Spill to Disk > Trigger the spilling > Query-level spilling | TiFlash Spill to Disk > Trigger the spilling > Query-level spilling > Example | TiFlash Spill to Disk > Notes`
- Source Line Ranges: `5-154`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `tidb`, `sql`
- Topic Tags: `spill-to-disk`, `memory-pressure`, `operator-level-spilling`, `query-level-spilling`, `hash-join`, `hash-aggregation`, `topn`, `sort`, `system-variables`, `memory-quota`, `spill-thresholds`, `query-termination`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0358_fb34bece8a`
- Source ID: `tidb-docs-8.1:tiflash/tiflash-spill-disk.md#tiflash-spill-to-disk`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `756e56eede6eed80a6e010364a17d4b1d247d9683c90581c3870a0d2e0a5de7b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiflash/tiflash-spill-disk#tiflash-spill-to-disk
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiflash/tiflash-spill-disk.md

## Retrieval Guidance

- Use When: Use this chunk when searching for how TiFlash spill to disk is triggered, which operators support spilling, the system variables for operator-level or query-level spilling, and the documented limits or error cases under memory pressure.
- Retrieval Keywords: TiFlash Spill to Disk, operator-level spilling, query-level spilling, tidb_max_bytes_before_tiflash_external_group_by, tidb_max_bytes_before_tiflash_external_join, tidb_max_bytes_before_tiflash_external_sort, tiflash_mem_quota_query_per_node, tiflash_query_spill_ratio, Hash Join operators with equi-join conditions, Hash Aggregation operators with GROUP BY keys, TopN operators, Sort operators in Window functions, Peak memory usage (total), Peak memory usage (for query), MemoryTracker.cpp:69, MemoryTracker.cpp:101, query termination, memory threshold errors
- Follow-up Guidance: The source also includes TPCH-100 SQL examples and notes that query-level spilling ignores individual operator thresholds when both tiflash_mem_quota_query_per_node and tiflash_query_spill_ratio are greater than 0.
- Classification Note: This chunk is classified as configuration because it centers on TiFlash spill-to-disk behavior controlled by documented system variables and threshold settings, with examples and notes about their effect.

## Official Source Content

# TiFlash Spill to Disk

This document introduces how TiFlash spills data to disk during computation.

Starting from v7.0.0, TiFlash supports spilling intermediate data to disk to relieve memory pressure. The following operators are supported:

* Hash Join operators with equi-join conditions
* Hash Aggregation operators with `GROUP BY` keys
* TopN operators, and Sort operators in Window functions
## Trigger the spilling

TiFlash provides two triggering mechanisms for spilling data to disk.

* Operator-level spilling: by specifying the data spilling threshold for each operator, you can control when TiFlash spills data of that operator to disk.
* Query-level spilling: by specifying the maximum memory usage of a query on a TiFlash node and the memory ratio for spilling, you can control when TiFlash spills data of supported operators in a query to disk as needed.
### Operator-level spilling

Starting from v7.0.0, TiFlash supports automatic spilling at the operator level. You can control the threshold of data spilling for each operator using the following system variables. When the memory usage of an operator exceeds the threshold, TiFlash triggers spilling for the operator.

* [`tidb_max_bytes_before_tiflash_external_group_by`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_max_bytes_before_tiflash_external_group_by-new-in-v700)
* [`tidb_max_bytes_before_tiflash_external_join`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_max_bytes_before_tiflash_external_join-new-in-v700)
* [`tidb_max_bytes_before_tiflash_external_sort`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_max_bytes_before_tiflash_external_sort-new-in-v700)
#### Example

This example constructs a SQL statement that consumes a lot of memory to demonstrate the spilling of the Hash Aggregation operator.

1. Prepare the environment. Create a TiFlash cluster with 2 nodes and import the TPCH-100 data.
2. Execute the following statements. These statements do not limit the memory usage of the Hash Aggregation operator with `GROUP BY` keys.

    ```sql
    SET tidb_max_bytes_before_tiflash_external_group_by = 0;
    SELECT
      l_orderkey,
      MAX(L_COMMENT),
      MAX(L_SHIPMODE),
      MAX(L_SHIPINSTRUCT),
      MAX(L_SHIPDATE),
      MAX(L_EXTENDEDPRICE)
    FROM lineitem
    GROUP BY l_orderkey
    HAVING SUM(l_quantity) > 314;
    ```

3. From the log of TiFlash, you can see that the query needs to consume 29.55 GiB of memory on a single TiFlash node:

    ```
    [DEBUG] [MemoryTracker.cpp:69] ["Peak memory usage (total): 29.55 GiB."] [source=MemoryTracker] [thread_id=468]
    ```

4. Execute the following statement. This statement limits the memory usage of the Hash Aggregation operator with `GROUP BY` keys to 10737418240 (10 GiB).

    ```sql
    SET tidb_max_bytes_before_tiflash_external_group_by = 10737418240;
    SELECT
      l_orderkey,
      MAX(L_COMMENT),
      MAX(L_SHIPMODE),
      MAX(L_SHIPINSTRUCT),
      MAX(L_SHIPDATE),
      MAX(L_EXTENDEDPRICE)
    FROM lineitem
    GROUP BY l_orderkey
    HAVING SUM(l_quantity) > 314;
    ```

5. From the log of TiFlash, you can see that by configuring `tidb_max_bytes_before_tiflash_external_group_by`, TiFlash triggers the spilling of intermediate results, significantly reducing the memory used by the query.

    ```
    [DEBUG] [MemoryTracker.cpp:69] ["Peak memory usage (total): 12.80 GiB."] [source=MemoryTracker] [thread_id=110]
    ```
### Query-level spilling

Starting from v7.4.0, TiFlash supports automatic spilling at the query level. You can control this feature using the following system variables:

* [`tiflash_mem_quota_query_per_node`](https://docs.pingcap.com/tidb/stable/system-variables#tiflash_mem_quota_query_per_node-new-in-v740): limits the maximum memory usage for a query on a TiFlash node.
* [`tiflash_query_spill_ratio`](https://docs.pingcap.com/tidb/stable/system-variables#tiflash_query_spill_ratio-new-in-v740): controls the memory ratio that triggers data spilling.

If both `tiflash_mem_quota_query_per_node` and `tiflash_query_spill_ratio` are set to values greater than 0, TiFlash automatically triggers spilling for supported operators in a query when the memory usage of a query exceeds `tiflash_mem_quota_query_per_node * tiflash_query_spill_ratio`.
#### Example

This example constructs a SQL statement that consumes a lot of memory to demonstrate the query-level spilling.

1. Prepare the environment. Create a TiFlash cluster with 2 nodes and import the TPCH-100 data.

2. Execute the following statements. These statements do not limit the memory usage of the query or the memory usage of the Hash Aggregation operator with `GROUP BY` keys.

    ```sql
    SET tidb_max_bytes_before_tiflash_external_group_by = 0;
    SET tiflash_mem_quota_query_per_node = 0;
    SET tiflash_query_spill_ratio = 0;
    SELECT
      l_orderkey,
      MAX(L_COMMENT),
      MAX(L_SHIPMODE),
      MAX(L_SHIPINSTRUCT),
      MAX(L_SHIPDATE),
      MAX(L_EXTENDEDPRICE)
    FROM lineitem
    GROUP BY l_orderkey
    HAVING SUM(l_quantity) > 314;
    ```

3. From the log of TiFlash, you can see that the query consumes 29.55 GiB of memory on a single TiFlash node:

    ```
    [DEBUG] [MemoryTracker.cpp:69] ["Peak memory usage (total): 29.55 GiB."] [source=MemoryTracker] [thread_id=468]
    ```

4. Execute the following statements. These statements limit the maximum memory usage of the query on a TiFlash node to 5 GiB.

    ```sql
    SET tiflash_mem_quota_query_per_node = 5368709120;
    SET tiflash_query_spill_ratio = 0.7;
    SELECT
      l_orderkey,
      MAX(L_COMMENT),
      MAX(L_SHIPMODE),
      MAX(L_SHIPINSTRUCT),
      MAX(L_SHIPDATE),
      MAX(L_EXTENDEDPRICE)
    FROM lineitem
    GROUP BY l_orderkey
    HAVING SUM(l_quantity) > 314;
    ```

5. From the log of TiFlash, you can see that by configuring query-level spilling, TiFlash triggers the spilling of intermediate results, significantly reducing the memory used by the query.

    ```
    [DEBUG] [MemoryTracker.cpp:101] ["Peak memory usage (for query): 3.94 GiB."] [source=MemoryTracker] [thread_id=1547]
    ```
## Notes

* When the Hash Aggregation operator does not have a `GROUP BY` key, it does not support spilling. Even if the Hash Aggregation operator contains a distinct aggregation function, it does not support spilling.
* Currently, the threshold for operator-level spilling is calculated for each operator separately. For a query containing two Hash Aggregation operators, if the query-level spilling is not configured and the threshold of the aggregation operator is set to 10 GiB, the two Hash Aggregation operators will only spill data when their respective memory usage exceeds 10 GiB.
* Currently, the Hash Aggregation operators and TopN/Sort operators use the merge aggregation and merge sort algorithm during the restore phase. Therefore, these two operators only trigger a single round of spill. If the memory demand is very high and the memory usage during the restore phase still exceeds the threshold, the spill will not be triggered again.
* Currently, the Hash Join operator uses the partition-based spill strategy. If the memory usage during the restore phase still exceeds the threshold, the spill will be triggered again. However, to control the scale of the spill, the number of rounds of spill is limited to three. If the memory usage during the restore phase still exceeds the threshold after the third round of spill, the spill will not be triggered again.
* When query-level spilling is configured (that is, both [`tiflash_mem_quota_query_per_node`](https://docs.pingcap.com/tidb/stable/system-variables#tiflash_mem_quota_query_per_node-new-in-v740) and [`tiflash_query_spill_ratio`](https://docs.pingcap.com/tidb/stable/system-variables#tiflash_query_spill_ratio-new-in-v740) are greater than 0), TiFlash ignores spilling thresholds of individual operators and automatically triggers spilling for relevant operators in a query based on the query-level spilling thresholds.
* Even when query-level spilling is configured, if none of the operators used in a query support spilling, the intermediate computation results of that query still cannot be spilled to disk. In this case, when the memory usage of that query exceeds the related threshold, TiFlash will return an error and terminate the query.
* Even when query-level spilling is configured and a query contains operators that support spilling, the query might still return an error due to exceeding memory thresholds in either of the following scenarios:
    - Other non-spilling operators in the query consume too much memory.
    - The spilling operators do not spill to disk timely.

  To address situations where spilling operators do not spill to disk in time, you can try reducing [`tiflash_query_spill_ratio`](https://docs.pingcap.com/tidb/stable/system-variables#tiflash_query_spill_ratio-new-in-v740) to avoid memory threshold errors.
