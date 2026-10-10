# Ways to read TiFlash replicas from TiDB

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/use-htap-cluster.md`
- Source Title: `Use an HTAP Cluster`
- Source Heading Path: `Use an HTAP Cluster > Use TiDB to read TiFlash replicas | Use an HTAP Cluster > Use TiDB to read TiFlash replicas > Smart selection | Use an HTAP Cluster > Use TiDB to read TiFlash replicas > Engine isolation | Use an HTAP Cluster > Use TiDB to read TiFlash replicas > Manual hint`
- Source Line Ranges: `34-80`
- Source Scope: `cloud`
- Primary Component: `tidb`
- Related Components: `tiflash`, `sql`
- Topic Tags: `query-routing`, `optimizer`, `explain-analyze`, `statistics`, `engine-isolation`, `session-variable`, `manual-hint`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0208_38b6852c52`
- Source ID: `tidb-docs-8.1:tidb-cloud/use-htap-cluster.md#use-tidb-to-read-tiflash-replicas`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `deada28282a187433966656ecc0d78a0cdcbbbad88429ae0ccced4d98c24efd9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/use-htap-cluster#use-tidb-to-read-tiflash-replicas
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/use-htap-cluster.md

## Retrieval Guidance

- Use When: Use this when the question is about how TiDB reads TiFlash replicas, how to verify a query is using TiFlash, or how to control TiFlash selection with optimizer behavior, engine isolation, or manual hints.
- Retrieval Keywords: Use TiDB to read TiFlash replicas, Smart selection, TiDB optimizer, cost estimation, explain analyze select count(*) from test.t, cop[tiflash], analyze table, Engine isolation, tidb_isolation_read_engines, set @@session.tidb_isolation_read_engines, tikv, tidb, tiflash, Manual hint, read_from_storage(tiflash[table_name])
- Follow-up Guidance: The source says that if queries have not selected a TiFlash replica, you can update statistics using the analyze table statement and then check the result using explain analyze.
- Classification Note: This is classified as performance because the content focuses on accelerating analytical computing by selecting TiFlash replicas through optimizer choice, isolation settings, and query hints.

## Official Source Content

## Use TiDB to read TiFlash replicas

After data is replicated to TiFlash, you can use one of the following three ways to read TiFlash replicas to accelerate your analytical computing.
### Smart selection

For tables with TiFlash replicas, the TiDB optimizer automatically determines whether to use TiFlash replicas based on the cost estimation. For example:

```sql
explain analyze select count(*) from test.t;
```

```sql
+--------------------------+---------+---------+--------------+---------------+----------------------------------------------------------------------+--------------------------------+-----------+------+
| id                       | estRows | actRows | task         | access object | execution info                                                       | operator info                  | memory    | disk |
+--------------------------+---------+---------+--------------+---------------+----------------------------------------------------------------------+--------------------------------+-----------+------+
| StreamAgg_9              | 1.00    | 1       | root         |               | time:83.8372ms, loops:2                                              | funcs:count(1)->Column#4       | 372 Bytes | N/A  |
| └─TableReader_17         | 1.00    | 1       | root         |               | time:83.7776ms, loops:2, rpc num: 1, rpc time:83.5701ms, proc keys:0 | data:TableFullScan_16          | 152 Bytes | N/A  |
|   └─TableFullScan_16     | 1.00    | 1       | cop[tiflash] | table:t       | time:43ms, loops:1                                                   | keep order:false, stats:pseudo | N/A       | N/A  |
+--------------------------+---------+---------+--------------+---------------+----------------------------------------------------------------------+--------------------------------+-----------+------+
```

`cop[tiflash]` means that the task will be sent to TiFlash for processing. If your queries have not selected a TiFlash replica, try to update the statistics using the `analyze table` statement, and then check the result using the `explain analyze` statement.
### Engine isolation

Engine isolation is to specify that all queries use a replica of the specified engine by configuring the `tidb_isolation_read_engines` variable. The optional engines are "tikv", "tidb" (indicates the internal memory table area of TiDB, which stores some TiDB system tables and cannot be actively used by users), and "tiflash".

```sql
set @@session.tidb_isolation_read_engines = "engine list separated by commas";
```
### Manual hint

Manual hint can force TiDB to use specified replicas for one or more specific tables on the premise of satisfying engine isolation. Here is an example of using the manual hint:

```sql
select /*+ read_from_storage(tiflash[table_name]) */ ... from table_name;
```

To learn more about TiFlash, refer to the documentation [here](https://docs.pingcap.com/tidb/stable/tiflash-overview/).
