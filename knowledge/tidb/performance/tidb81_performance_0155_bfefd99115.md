# Execute query and compare Runtime Filter performance

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/runtime-filter.md`
- Source Title: `Runtime Filter`
- Source Heading Path: `Runtime Filter > Use Runtime Filter > Step 3. Execute the query | Runtime Filter > Use Runtime Filter > Step 4. Performance comparison`
- Source Line Ranges: `133-182`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `sql`, `tidb`
- Topic Tags: `runtime filter`, `explain plan`, `hash join`, `table scan`, `mpp`, `query execution`, `performance comparison`, `analyze`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0155_bfefd99115`
- Source ID: `tidb-docs-8.1:runtime-filter.md#step-3-execute-the-query`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3f13411cf612e23db349688b0a67047cdeefb766d83b5e9a34a81115dcf51298`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/runtime-filter#step-3-execute-the-query
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/runtime-filter.md

## Retrieval Guidance

- Use When: Use this chunk when you need the EXPLAIN plan and example SQL that show Runtime Filter on HashJoin and TableScan, or when comparing the query time with and without Runtime Filter in the TPC-DS example.
- Retrieval Keywords: EXPLAIN SELECT cs_ship_date_sk FROM catalog_sales, date_dim WHERE d_date = '2002-2-01' AND cs_ship_date_sk = d_date_sk, runtime filter:0[IN], HashJoin, TableFullScan, TableScan, mpp[tiflash], ANALYZE statement, 0.38 seconds to 0.17 seconds, 50 GB TPC-DS data
- Follow-up Guidance: You can use the ANALYZE statement to view the execution time of each operator after Runtime Filter takes effect.
- Classification Note: The content is a performance example for TiFlash showing how Runtime Filter appears in the execution plan and how it changes query time in a TPC-DS query.

## Official Source Content

### Step 3. Execute the query

Before executing the query, use the [`EXPLAIN` statement](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-explain) to show the execution plan and check whether Runtime Filter has taken effect.

```sql
EXPLAIN SELECT cs_ship_date_sk FROM catalog_sales, date_dim
WHERE d_date = '2002-2-01' AND
     cs_ship_date_sk = d_date_sk;
```

When Runtime Filter takes effect, the corresponding Runtime Filter is mounted on the `HashJoin` node and the `TableScan` node, indicating that Runtime Filter is applied successfully.

```
TableFullScan: runtime filter:0[IN] -> tpcds50.catalog_sales.cs_ship_date_sk
HashJoin: runtime filter:0[IN] <- tpcds50.date_dim.d_date_sk |
```

The complete query execution plan is as follows:

```
+----------------------------------------+-------------+--------------+---------------------+-----------------------------------------------------------------------------------------------------------------------------------------------+
| id                                     | estRows     | task         | access object       | operator info                                                                                                                                 |
+----------------------------------------+-------------+--------------+---------------------+-----------------------------------------------------------------------------------------------------------------------------------------------+
| TableReader_53                         | 37343.19    | root         |                     | MppVersion: 1, data:ExchangeSender_52                                                                                                         |
| └─ExchangeSender_52                    | 37343.19    | mpp[tiflash] |                     | ExchangeType: PassThrough                                                                                                                     |
|   └─Projection_51                      | 37343.19    | mpp[tiflash] |                     | tpcds50.catalog_sales.cs_ship_date_sk                                                                                                         |
|     └─HashJoin_48                      | 37343.19    | mpp[tiflash] |                     | inner join, equal:[eq(tpcds50.date_dim.d_date_sk, tpcds50.catalog_sales.cs_ship_date_sk)], runtime filter:0[IN] <- tpcds50.date_dim.d_date_sk |
|       ├─ExchangeReceiver_29(Build)     | 1.00        | mpp[tiflash] |                     |                                                                                                                                               |
|       │ └─ExchangeSender_28            | 1.00        | mpp[tiflash] |                     | ExchangeType: Broadcast, Compression: FAST                                                                                                    |
|       │   └─TableFullScan_26           | 1.00        | mpp[tiflash] | table:date_dim      | pushed down filter:eq(tpcds50.date_dim.d_date, 2002-02-01 00:00:00.000000), keep order:false                                                  |
|       └─Selection_31(Probe)            | 71638034.00 | mpp[tiflash] |                     | not(isnull(tpcds50.catalog_sales.cs_ship_date_sk))                                                                                            |
|         └─TableFullScan_30             | 71997669.00 | mpp[tiflash] | table:catalog_sales | pushed down filter:empty, keep order:false, runtime filter:0[IN] -> tpcds50.catalog_sales.cs_ship_date_sk                                     |
+----------------------------------------+-------------+--------------+---------------------+-----------------------------------------------------------------------------------------------------------------------------------------------+
9 rows in set (0.01 sec)
```

Now, execute the SQL query, and Runtime Filter is applied.

```sql
SELECT cs_ship_date_sk FROM catalog_sales, date_dim
WHERE d_date = '2002-2-01' AND
     cs_ship_date_sk = d_date_sk;
```
### Step 4. Performance comparison

This example uses the 50 GB TPC-DS data. After Runtime Filter is enabled, the query time is reduced from 0.38 seconds to 0.17 seconds, and efficiency is improved by 50%. You can use the `ANALYZE` statement to view the execution time of each operator after Runtime Filter takes effect.

The following is the execution information of the query when Runtime Filter is not enabled:
