# CLUSTER_SLOW_QUERY query pushdown and aggregation hint

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/information-schema/information-schema-slow-query.md`
- Source Title: `SLOW_QUERY`
- Source Heading Path: `SLOW_QUERY > CLUSTER_SLOW_QUERY table`
- Source Line Ranges: `234-260`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: none
- Topic Tags: `pushdown`, `execution-plan`, `aggregation`, `sql-hint`, `system-tables`, `slow-query`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0120_54e539b613`
- Source ID: `tidb-docs-8.1:information-schema/information-schema-slow-query.md#cluster-slow-query-table`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0e5885770bf2c6b169ce13ecc208e23a7c586b1768557970b8bbe438334f6bec`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/information-schema/information-schema-slow-query#cluster-slow-query-table
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/information-schema/information-schema-slow-query.md

## Retrieval Guidance

- Use When: Use this chunk when you need official behavior for query pushdown on CLUSTER_SLOW_QUERY or the documented AGG_TO_COP() hint example for aggregation on a cluster system table.
- Retrieval Keywords: CLUSTER_SLOW_QUERY pushdown, cluster system table queried, DESC SELECT COUNT(*) FROM CLUSTER_SLOW_QUERY WHERE user = 'u1', Selection_12, cop[tidb], TableFullScan_11, StreamAgg_7, AGG_TO_COP(), SELECT /*+ AGG_TO_COP() */ COUNT(*) FROM CLUSTER_SLOW_QUERY GROUP BY user, system tables statistics not collected, aggregation operators cannot be pushed down
- Follow-up Guidance: The source also notes that because statistics of the system tables are not collected, some aggregation operators might not be pushed down, and it shows `SELECT /*+ AGG_TO_COP() */ COUNT(*) FROM CLUSTER_SLOW_QUERY GROUP BY user;` as an example.
- Classification Note: This is a performance chunk because it describes pushdown behavior, execution plan operators, and an aggregation hint that can affect slow execution on CLUSTER_SLOW_QUERY.

## Official Source Content

When the cluster system table is queried, TiDB does not obtain data from all nodes, but pushes down the related calculation to other nodes. The execution plan is as follows:

```sql
DESC SELECT COUNT(*) FROM CLUSTER_SLOW_QUERY WHERE user = 'u1';
```

The output is as follows:

```sql
+----------------------------+----------+-----------+--------------------------+------------------------------------------------------+
| id                         | estRows  | task      | access object            | operator info                                        |
+----------------------------+----------+-----------+--------------------------+------------------------------------------------------+
| StreamAgg_7                | 1.00     | root      |                          | funcs:count(1)->Column#75                            |
| └─TableReader_13           | 10.00    | root      |                          | data:Selection_12                                    |
|   └─Selection_12           | 10.00    | cop[tidb] |                          | eq(INFORMATION_SCHEMA.cluster_slow_query.user, "u1") |
|     └─TableFullScan_11     | 10000.00 | cop[tidb] | table:CLUSTER_SLOW_QUERY | keep order:false, stats:pseudo                       |
+----------------------------+----------+-----------+--------------------------+------------------------------------------------------+
4 rows in set (0.00 sec)
```

In the preceding execution plan, the `user = u1` condition is pushed down to other (`cop`) TiDB nodes, and the aggregate operator is also pushed down (the `StreamAgg` operator in the graph).

Currently, because statistics of the system tables are not collected, sometimes some aggregation operators cannot be pushed down, which results in slow execution. In this case, you can manually specify the SQL HINT to push down the aggregation operators. For example:

```sql
SELECT /*+ AGG_TO_COP() */ COUNT(*) FROM CLUSTER_SLOW_QUERY GROUP BY user;
```
