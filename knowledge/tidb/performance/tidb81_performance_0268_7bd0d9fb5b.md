# TiFlash MPP algorithms and broadcast join controls

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiflash/use-tiflash-mpp-mode.md`
- Source Title: `Use TiFlash MPP Mode`
- Source Heading Path: `Use TiFlash MPP Mode > Algorithm support for the MPP mode`
- Source Line Ranges: `90-121`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `tidb`, `sql`
- Topic Tags: `mpp`, `hash-join`, `hash-aggregation`, `broadcast-join`, `shuffle`, `exchange-operator`, `explain`, `session-variables`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0268_7bd0d9fb5b`
- Source ID: `tidb-docs-8.1:tiflash/use-tiflash-mpp-mode.md#algorithm-support-for-the-mpp-mode`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1fc25484ae42a2b06a1643f3c0dbf0eafd082026019cb6caf355de0ff990fa0b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiflash/use-tiflash-mpp-mode#algorithm-support-for-the-mpp-mode
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiflash/use-tiflash-mpp-mode.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving which physical algorithms TiFlash MPP mode supports, how to confirm MPP in an `EXPLAIN` plan, or how Broadcast Hash Join selection is controlled by broadcast join variables.
- Retrieval Keywords: Algorithm support for the MPP mode, Broadcast Hash Join, Shuffled Hash Join, Shuffled Hash Aggregation, Union All, TopN, Limit, EXPLAIN, ExchangeSender, ExchangeReceiver, mpp[tiflash], ExchangeType: Broadcast, HashJoin, HashAgg, TableReader, tidb_broadcast_join_threshold_size, tidb_broadcast_join_threshold_count, tidb_prefer_broadcast_join_by_exchange_data_size, minimum overhead of network transmission
- Follow-up Guidance: If `tidb_prefer_broadcast_join_by_exchange_data_size` is enabled, TiDB compares the exchanged network data size of `Broadcast Hash Join` and `Shuffled Hash Join` and the threshold variables no longer take effect.
- Classification Note: The official content is classified as performance because it describes MPP execution algorithms, execution-plan indicators, and variables that affect join strategy selection and network exchange overhead.

## Official Source Content

## Algorithm support for the MPP mode

The MPP mode supports these physical algorithms: Broadcast Hash Join, Shuffled Hash Join, Shuffled Hash Aggregation, Union All, TopN, and Limit. The optimizer automatically determines which algorithm to be used in a query. To check the specific query execution plan, you can execute the `EXPLAIN` statement. If the result of the `EXPLAIN` statement shows ExchangeSender and ExchangeReceiver operators, it indicates that the MPP mode has taken effect.

The following statement takes the table structure in the TPC-H test set as an example:

```sql
explain select count(*) from customer c join nation n on c.c_nationkey=n.n_nationkey;
+------------------------------------------+------------+--------------+---------------+----------------------------------------------------------------------------+
| id                                       | estRows    | task         | access object | operator info                                                              |
+------------------------------------------+------------+--------------+---------------+----------------------------------------------------------------------------+
| HashAgg_23                               | 1.00       | root         |               | funcs:count(Column#16)->Column#15                                          |
| └─TableReader_25                         | 1.00       | root         |               | data:ExchangeSender_24                                                     |
|   └─ExchangeSender_24                    | 1.00       | mpp[tiflash] |               | ExchangeType: PassThrough                                                  |
|     └─HashAgg_12                         | 1.00       | mpp[tiflash] |               | funcs:count(1)->Column#16                                                  |
|       └─HashJoin_17                      | 3000000.00 | mpp[tiflash] |               | inner join, equal:[eq(tpch.nation.n_nationkey, tpch.customer.c_nationkey)] |
|         ├─ExchangeReceiver_21(Build)     | 25.00      | mpp[tiflash] |               |                                                                            |
|         │ └─ExchangeSender_20            | 25.00      | mpp[tiflash] |               | ExchangeType: Broadcast                                                    |
|         │   └─TableFullScan_18           | 25.00      | mpp[tiflash] | table:n       | keep order:false                                                           |
|         └─TableFullScan_22(Probe)        | 3000000.00 | mpp[tiflash] | table:c       | keep order:false                                                           |
+------------------------------------------+------------+--------------+---------------+----------------------------------------------------------------------------+
9 rows in set (0.00 sec)
```

In the example execution plan, the `ExchangeReceiver` and `ExchangeSender` operators are included. The execution plan indicates that after the `nation` table is read, the `ExchangeSender` operator broadcasts the table to each node, the `HashJoin` and `HashAgg` operations are performed on the `nation` table and the `customer` table, and then the results are returned to TiDB.

TiFlash provides the following 3 global/session variables to control whether to use Broadcast Hash Join:

- [`tidb_broadcast_join_threshold_size`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_broadcast_join_threshold_size-new-in-v50): The unit of the value is bytes. If the table size (in the unit of bytes) is less than the value of the variable, the Broadcast Hash Join algorithm is used. Otherwise, the Shuffled Hash Join algorithm is used.
- [`tidb_broadcast_join_threshold_count`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_broadcast_join_threshold_count-new-in-v50): The unit of the value is rows. If the objects of the join operation belong to a subquery, the optimizer cannot estimate the size of the subquery result set, so the size is determined by the number of rows in the result set. If the estimated number of rows in the subquery is less than the value of this variable, the Broadcast Hash Join algorithm is used. Otherwise, the Shuffled Hash Join algorithm is used.
- [`tidb_prefer_broadcast_join_by_exchange_data_size`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_prefer_broadcast_join_by_exchange_data_size-new-in-v710): controls whether to use the algorithm with the minimum overhead of network transmission. If this variable is enabled, TiDB estimates the size of the data to be exchanged in the network using `Broadcast Hash Join` and `Shuffled Hash Join` respectively, and then chooses the one with the smaller size. [`tidb_broadcast_join_threshold_count`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_broadcast_join_threshold_count-new-in-v50) and [`tidb_broadcast_join_threshold_size`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_broadcast_join_threshold_size-new-in-v50) will not take effect after this variable is enabled.
