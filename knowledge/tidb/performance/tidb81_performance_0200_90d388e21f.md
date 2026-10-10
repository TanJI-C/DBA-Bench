# Compare TiKV and TiFlash query performance with EXPLAIN ANALYZE

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tidb-cloud-htap-quickstart.md`
- Source Title: `TiDB Cloud HTAP Quick Start`
- Source Heading Path: `TiDB Cloud HTAP Quick Start > Steps > Step 3. Compare the query performance between row-based storage and columnar storage | TiDB Cloud HTAP Quick Start > Learn more`
- Source Line Ranges: `73-158`
- Source Scope: `cloud`
- Primary Component: `tiflash`
- Related Components: `tidb`, `tikv`, `cloud`, `sql`
- Topic Tags: `performance-comparison`, `explain-analyze`, `optimizer-hints`, `tikv`, `tiflash`, `mpp`, `execution-statistics`, `query-plan`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0200_90d388e21f`
- Source ID: `tidb-docs-8.1:tidb-cloud/tidb-cloud-htap-quickstart.md#step-3-compare-the-query-performance-between-row-based-storage-and-columnar-storage`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0ec0d5d5899fc530d6b732fa100ce21481f3ed6166562610b7742f9361711cde`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-htap-quickstart#step-3-compare-the-query-performance-between-row-based-storage-and-columnar-storage
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tidb-cloud-htap-quickstart.md

## Retrieval Guidance

- Use When: Use this chunk when the user wants to compare TiKV and TiFlash execution statistics for the same query in TiDB Cloud by using EXPLAIN ANALYZE and the READ_FROM_STORAGE optimizer hint.
- Retrieval Keywords: Compare the query performance between row-based storage and columnar storage, EXPLAIN ANALYZE, READ_FROM_STORAGE(TIKV[games]), TiKV execution statistics, TiFlash execution statistics, execution info column, mpp[tiflash], cop[tikv], TableFullScan_23, TableFullScan_14, optimizer hint --comments, MppVersion: 1
- Follow-up Guidance: It notes that for tables with TiFlash replicas, the TiDB optimizer automatically chooses TiKV or TiFlash based on cost estimation, and it also notes that TiKV might be much faster on a repeated query because it can reuse its cache.
- Classification Note: This is classified as a performance chunk because the content focuses on measuring and comparing query execution behavior and timing between TiKV row-based storage and TiFlash columnar storage.

## Official Source Content

### Step 3. Compare the query performance between row-based storage and columnar storage

In this step, you can compare the execution statistics between TiKV (row-based storage) and TiFlash (columnar storage).

- To get the execution statistics of this query using TiKV, execute the following statement:

    ```sql
    EXPLAIN ANALYZE SELECT /*+ READ_FROM_STORAGE(TIKV[games]) */
      YEAR(`release_date`) AS `release_year`,
      COUNT(*) AS `games_released`,
      AVG(`price`) AS `average_price`,
      AVG(`average_playtime_forever`) AS `average_playtime`
    FROM
      `games`
    GROUP BY
      `release_year`
    ORDER BY
      `release_year` DESC;
    ```

    For tables with TiFlash replicas, the TiDB optimizer automatically determines whether to use either TiKV or TiFlash replicas based on the cost estimation. In the preceding `EXPLAIN ANALYZE` statement, the `/*+ READ_FROM_STORAGE(TIKV[games]) */` hint is used to force the optimizer to choose TiKV so you can check the execution statistics of TiKV.

    > **Note:**
    >
    > MySQL command-line clients earlier than 5.7.7 strip optimizer hints by default. If you are using the `Hint` syntax in these earlier versions, add the `--comments` option when starting the client. For example: `mysql -h 127.0.0.1 -P 4000 -uroot --comments`.

    In the output, you can get the execution time from the `execution info` column.

    ```sql
    id                         | estRows  | actRows | task      | access object | execution info                             | operator info                                 | memory  | disk    
    ---------------------------+----------+---------+-----------+---------------+--------------------------------------------+-----------------------------------------------+---------+---------
    Sort_5                     | 4019.00  | 28      | root      |               | time:672.7ms, loops:2, RU:1159.679690      | Column#36:desc                                | 18.0 KB | 0 Bytes 
    └─Projection_7             | 4019.00  | 28      | root      |               | time:672.7ms, loops:6, Concurrency:5       | year(game.games.release_date)->Column#36, ... | 35.5 KB | N/A     
      └─HashAgg_15             | 4019.00  | 28      | root      |               | time:672.6ms, loops:6, partial_worker:...  | group by:Column#38, funcs:count(Column#39)... | 56.7 KB | N/A     
        └─TableReader_16       | 4019.00  | 28      | root      |               | time:672.4ms, loops:2, cop_task: {num:...  | data:HashAgg_9                                | 3.60 KB | N/A     
          └─HashAgg_9          | 4019.00  | 28      | cop[tikv] |               | tikv_task:{proc max:300ms, min:0s, avg...  | group by:year(game.games.release_date), ...   | N/A     | N/A     
            └─TableFullScan_14 | 68223.00 | 68223   | cop[tikv] | table:games   | tikv_task:{proc max:290ms, min:0s, avg...  | keep order:false                              | N/A     | N/A     
    (6 rows)
    ```

- To get the execution statistics of this query using TiFlash, execute the following statement:

    ```sql
    EXPLAIN ANALYZE SELECT
      YEAR(`release_date`) AS `release_year`,
      COUNT(*) AS `games_released`,
      AVG(`price`) AS `average_price`,
      AVG(`average_playtime_forever`) AS `average_playtime`
    FROM
      `games`
    GROUP BY
      `release_year`
    ORDER BY
      `release_year` DESC;
    ```

    In the output, you can get the execution time from the `execution info` column.

    ```sql
    id                                   | estRows  | actRows | task         | access object | execution info                                        | operator info                              | memory  | disk    
    -------------------------------------+----------+---------+--------------+---------------+-------------------------------------------------------+--------------------------------------------+---------+---------
    Sort_5                               | 4019.00  | 28      | root         |               | time:222.2ms, loops:2, RU:25.609675                   | Column#36:desc                             | 3.77 KB | 0 Bytes 
    └─TableReader_39                     | 4019.00  | 28      | root         |               | time:222.1ms, loops:2, cop_task: {num: 2, max: 0s,... | MppVersion: 1, data:ExchangeSender_38      | 4.64 KB | N/A     
      └─ExchangeSender_38                | 4019.00  | 28      | mpp[tiflash] |               | tiflash_task:{time:214.8ms, loops:1, threads:1}       | ExchangeType: PassThrough                  | N/A     | N/A     
        └─Projection_8                   | 4019.00  | 28      | mpp[tiflash] |               | tiflash_task:{time:214.8ms, loops:1, threads:1}       | year(game.games.release_date)->Column#3... | N/A     | N/A     
          └─Projection_34                | 4019.00  | 28      | mpp[tiflash] |               | tiflash_task:{time:214.8ms, loops:1, threads:1}       | Column#33, div(Column#34, cast(case(eq(... | N/A     | N/A     
            └─HashAgg_35                 | 4019.00  | 28      | mpp[tiflash] |               | tiflash_task:{time:214.8ms, loops:1, threads:1}       | group by:Column#63, funcs:sum(Column#64... | N/A     | N/A     
              └─ExchangeReceiver_37      | 4019.00  | 28      | mpp[tiflash] |               | tiflash_task:{time:214.8ms, loops:1, threads:8}       |                                            | N/A     | N/A     
                └─ExchangeSender_36      | 4019.00  | 28      | mpp[tiflash] |               | tiflash_task:{time:210.6ms, loops:1, threads:1}       | ExchangeType: HashPartition, Compressio... | N/A     | N/A     
                  └─HashAgg_33           | 4019.00  | 28      | mpp[tiflash] |               | tiflash_task:{time:210.6ms, loops:1, threads:1}       | group by:Column#75, funcs:count(1)->Col... | N/A     | N/A     
                    └─Projection_40      | 68223.00 | 68223   | mpp[tiflash] |               | tiflash_task:{time:210.6ms, loops:2, threads:8}       | game.games.price, game.games.price, gam... | N/A     | N/A     
                      └─TableFullScan_23 | 68223.00 | 68223   | mpp[tiflash] | table:games   | tiflash_task:{time:210.6ms, loops:2, threads:8}, ...  | keep order:false                           | N/A     | N/A     
    (11 rows)
    ```

> **Note:**
>
> Because the size of sample data is small and the query in this document is very simple, if you have already forced the optimizer to choose TiKV for this query and run the same query again, TiKV will reuse its cache, so the query might be much faster. If the data is updated frequently, the cache will be missed.
## Learn more

- [TiFlash Overview](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-overview)
- [Create TiFlash Replicas](https://docs.pingcap.com/tidb/stable/tiflash/create-tiflash-replicas)
- [Read Data from TiFlash](https://docs.pingcap.com/tidb/stable/tiflash/use-tidb-to-read-tiflash)
- [Use MPP Mode](https://docs.pingcap.com/tidb/stable/tiflash/use-tiflash-mpp-mode)
- [Supported Push-down Calculations](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-supported-pushdown-calculations)
