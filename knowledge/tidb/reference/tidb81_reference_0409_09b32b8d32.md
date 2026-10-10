# CLUSTER_SLOW_QUERY table overview

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/information-schema/information-schema-slow-query.md`
- Source Title: `SLOW_QUERY`
- Source Heading Path: `SLOW_QUERY > CLUSTER_SLOW_QUERY table`
- Source Line Ranges: `126-145`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `information_schema`, `cluster_slow_query`, `slow_log`, `instance_column`, `cluster_queries`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0409_09b32b8d32`
- Source ID: `tidb-docs-8.1:information-schema/information-schema-slow-query.md#cluster-slow-query-table`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3d9942d9246e8d77f9fcd9ce2efa1f123b74de885bf2fc79b0270346f70b7362`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/information-schema/information-schema-slow-query#cluster-slow-query-table
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/information-schema/information-schema-slow-query.md

## Retrieval Guidance

- Use When: Use this content when you need the cluster-wide slow query table and want to know how `CLUSTER_SLOW_QUERY` differs from `SLOW_QUERY`.
- Retrieval Keywords: CLUSTER_SLOW_QUERY, DESC CLUSTER_SLOW_QUERY, slow query information of all nodes in the cluster, INSTANCE column, TiDB node address, use the CLUSTER_SLOW_QUERY table the way you do with SLOW_QUERY, parsing result of the TiDB slow log files
- Follow-up Guidance: The source points to the Slow Query Log Document for how to use this table to identify problematic statements and improve query performance.
- Classification Note: This is reference content because it describes the purpose of `CLUSTER_SLOW_QUERY`, its cluster scope, and its schema difference from `SLOW_QUERY` through the added `INSTANCE` column.

## Official Source Content

## CLUSTER_SLOW_QUERY table

The `CLUSTER_SLOW_QUERY` table provides the slow query information of all nodes in the cluster, which is the parsing result of the TiDB slow log files. You can use the `CLUSTER_SLOW_QUERY` table the way you do with `SLOW_QUERY`. The table schema of the `CLUSTER_SLOW_QUERY` table differs from that of the `SLOW_QUERY` table in that an `INSTANCE` column is added to `CLUSTER_SLOW_QUERY`. The `INSTANCE` column represents the TiDB node address of the row information on the slow query.

> **Note:**
>
> This table is not available on [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

For how to use this table to identify problematic statements and improve query performance, see [Slow Query Log Document](https://docs.pingcap.com/tidb/stable/identify-slow-queries).

```sql
DESC CLUSTER_SLOW_QUERY;
```

The output is as follows:
