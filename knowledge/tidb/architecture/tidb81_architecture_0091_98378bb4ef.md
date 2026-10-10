# HTAP cluster overview and TiFlash replica setup

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/use-htap-cluster.md`
- Source Title: `Use an HTAP Cluster`
- Source Heading Path: `Use an HTAP Cluster`
- Source Line Ranges: `5-33`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`, `tikv`, `tiflash`, `sql`
- Topic Tags: `htap`, `tiflash-replica`, `replication`, `cluster-scaling`, `serverless`, `sql`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0091_98378bb4ef`
- Source ID: `tidb-docs-8.1:tidb-cloud/use-htap-cluster.md#use-an-htap-cluster`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f35cb8a0a209fc0e902b8ebfe7c7995d1aa91db5b5412dddb92c3def2bb1b247`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/use-htap-cluster#use-an-htap-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/use-htap-cluster.md

## Retrieval Guidance

- Use When: Use this when the question is about what an HTAP cluster in TiDB Cloud includes, how TiKV data is replicated to TiFlash, how to add TiFlash nodes, or how to create and check a TiFlash replica for a table.
- Retrieval Keywords: HTAP cluster, TiDB Cloud, TiKV, TiFlash, row-based storage engine, columnar storage, Raft consensus algorithm, real time replication, TiFlash nodes, scaling the cluster, TiDB Cloud Serverless, TiFlash is always enabled, ALTER TABLE table_name SET TIFLASH REPLICA 1, SET TIFLASH REPLICA 0, information_schema.tiflash_replica, SELECT * FROM information_schema.tiflash_replica WHERE TABLE_SCHEMA = '<db_name>' and TABLE_NAME = '<table_name>'
- Follow-up Guidance: The source also shows that the replica count must be no larger than the number of TiFlash nodes and that setting the replica count to 0 deletes the replica in TiFlash.
- Classification Note: This is classified as architecture because the content describes the HTAP cluster composition, replication path between TiKV and TiFlash, and table-level TiFlash replica setup in TiDB Cloud.

## Official Source Content

# Use an HTAP Cluster

[HTAP](https://en.wikipedia.org/wiki/Hybrid_transactional/analytical_processing) means Hybrid Transactional/Analytical Processing. The HTAP cluster in TiDB Cloud is composed of [TiKV](https://tikv.org), a row-based storage engine designed for transactional processing, and [TiFlash](https://docs.pingcap.com/tidb/stable/tiflash-overview), a columnar storage designed for analytical processing. Your application data is first stored in TiKV and then replicated to TiFlash via the Raft consensus algorithm. So it is real time replication from the row store to the columnar store.

With TiDB Cloud, you can create an HTAP cluster easily by specifying one or more TiFlash nodes according to your HTAP workload. If the TiFlash node count is not specified when you create the cluster or you want to add more TiFlash nodes, you can change the node count by [scaling the cluster](https://docs.pingcap.com/tidb/stable/tidb-cloud/scale-tidb-cluster).

> **Note:**
>
> TiFlash is always enabled for TiDB Cloud Serverless clusters. You cannot disable it.

TiKV data is not replicated to TiFlash by default. You can select which table to replicate to TiFlash using the following SQL statement:

```sql
ALTER TABLE table_name SET TIFLASH REPLICA 1;
```

The number of replicas count must be no larger than the number of TiFlash nodes. Setting the number of replicas to `0` means deleting the replica in TiFlash.

To check the replication progress, use the following command:

```sql
SELECT * FROM information_schema.tiflash_replica WHERE TABLE_SCHEMA = '<db_name>' and TABLE_NAME = '<table_name>';
```
