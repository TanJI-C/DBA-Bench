# MPPVersion and Exchange compression fields in execution plans

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/explain-mpp.md`
- Source Title: `Explain Statements in the MPP Mode`
- Source Heading Path: `Explain Statements in the MPP Mode > MPP version and exchange data compression`
- Source Line Ranges: `174-202`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `tiflash`
- Topic Tags: `mpp version`, `exchange compression`, `execution plan`, `system variables`, `exchange sender`, `hash partition`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0264_82be6947a1`
- Source ID: `tidb-docs-8.1:explain-mpp.md#mpp-version-and-exchange-data-compression`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5c86ef58adca6d6347421109735efb5cd0dda0f9fcf1c6d4fa7a4f7d53811e97`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/explain-mpp#mpp-version-and-exchange-data-compression
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/explain-mpp.md

## Retrieval Guidance

- Use When: Use this chunk when reading an MPP execution plan and you need to identify the `MPPVersion` field or the `Compression` field shown for `Exchange` operators.
- Retrieval Keywords: MPPVersion, Compression, mpp_version, mpp_exchange_compression_mode, ExchangeSender_33, ExchangeType: HashPartition, ExchangeType: PassThrough, Compression: FAST, stream_count: 20, mpp[tiflash]
- Follow-up Guidance: The source states that `MppVersion` can be set through `mpp_version`, `Compression` can be set through `mpp_exchange_compression_mode`, and the `Compression` field is not displayed when data compression is not enabled.
- Classification Note: This is reference content because it describes execution plan fields and their meanings for MPP version and exchange data compression.

## Official Source Content

## MPP version and exchange data compression

Starting from v6.6.0, the new fields `MPPVersion` and `Compression` are added to the MPP execution plan.

- `MppVersion`: The version number of the MPP execution plan, which can be set through the system variable [`mpp_version`](https://docs.pingcap.com/tidb/stable/system-variables#mpp_version-new-in-v660).
- `Compression`: The data compression mode of the `Exchange` operator, which can be set through the system variable [`mpp_exchange_compression_mode`](https://docs.pingcap.com/tidb/stable/system-variables#mpp_exchange_compression_mode-new-in-v660). If data compression is not enabled, this field is not displayed in the execution plan.

See the following example:

```sql
mysql > EXPLAIN SELECT COUNT(*) AS count_order FROM lineitem GROUP BY l_returnflag, l_linestatus ORDER BY l_returnflag, l_linestatus;

+----------------------------------------+--------------+--------------+----------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| id                                     | estRows      | task         | access object  | operator info                                                                                                                                                                                                                                                                        |
+----------------------------------------+--------------+--------------+----------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Projection_6                           | 3.00         | root         |                | Column#18                                                                                                                                                                                                                                                                            |
| └─Sort_8                               | 3.00         | root         |                | tpch100.lineitem.l_returnflag, tpch100.lineitem.l_linestatus                                                                                                                                                                                                                         |
|   └─TableReader_36                     | 3.00         | root         |                | MppVersion: 1, data:ExchangeSender_35                                                                                                                                                                                                                                                |
|     └─ExchangeSender_35                | 3.00         | mpp[tiflash] |                | ExchangeType: PassThrough                                                                                                                                                                                                                                                            |
|       └─Projection_31                  | 3.00         | mpp[tiflash] |                | Column#18, tpch100.lineitem.l_returnflag, tpch100.lineitem.l_linestatus                                                                                                                                                                                                              |
|         └─HashAgg_32                   | 3.00         | mpp[tiflash] |                | group by:tpch100.lineitem.l_linestatus, tpch100.lineitem.l_returnflag, funcs:sum(Column#23)->Column#18, funcs:firstrow(tpch100.lineitem.l_returnflag)->tpch100.lineitem.l_returnflag, funcs:firstrow(tpch100.lineitem.l_linestatus)->tpch100.lineitem.l_linestatus, stream_count: 20 |
|           └─ExchangeReceiver_34        | 3.00         | mpp[tiflash] |                | stream_count: 20                                                                                                                                                                                                                                                                     |
|             └─ExchangeSender_33        | 3.00         | mpp[tiflash] |                | ExchangeType: HashPartition, Compression: FAST, Hash Cols: [name: tpch100.lineitem.l_returnflag, collate: utf8mb4_bin], [name: tpch100.lineitem.l_linestatus, collate: utf8mb4_bin], stream_count: 20                                                                                |
|               └─HashAgg_14             | 3.00         | mpp[tiflash] |                | group by:tpch100.lineitem.l_linestatus, tpch100.lineitem.l_returnflag, funcs:count(1)->Column#23                                                                                                                                                                                     |
|                 └─TableFullScan_30     | 600037902.00 | mpp[tiflash] | table:lineitem | keep order:false                                                                                                                                                                                                                                                                     |
+----------------------------------------+--------------+--------------+----------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
```

In the preceding execution plan result, TiDB uses an MPP execution plan of version `1` to build `TableReader`. The `ExchangeSender` operator of the `HashPartition` type uses the `FAST` data compression mode. Data compression is not enabled for the `ExchangeSender` operator of the `PassThrough` type.
