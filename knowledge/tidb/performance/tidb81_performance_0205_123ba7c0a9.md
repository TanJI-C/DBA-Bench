# Troubleshoot bottlenecks outside the TiDB cluster

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tidb-cloud-tune-performance-overview.md`
- Source Title: `Overview for Analyzing and Tuning Performance`
- Source Heading Path: `Overview for Analyzing and Tuning Performance > Troubleshoot bottlenecks in user response time > Bottlenecks outside the TiDB cluster`
- Source Line Ranges: `58-71`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`, `tikv`, `sql`
- Topic Tags: `external-bottlenecks`, `latency`, `throughput`, `version-check`, `prepared-plan-cache`, `jdbc`, `token-limit`, `client-side-caching`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0205_123ba7c0a9`
- Source ID: `tidb-docs-8.1:tidb-cloud/tidb-cloud-tune-performance-overview.md#bottlenecks-outside-the-tidb-cluster`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2da9d5f34b3977c6912e5402f68cb68ea0fe87945168bf58e89249e5557f73aa`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-tune-performance-overview#bottlenecks-outside-the-tidb-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tidb-cloud-tune-performance-overview.md

## Retrieval Guidance

- Use When: Use this chunk when Latency(P80) on the Overview tab is much lower than the P80 value for user response time and you need the documented checks for bottlenecks outside the TiDB cluster.
- Retrieval Keywords: Bottlenecks outside the TiDB cluster, Latency(P80), Overview tab, P80 value for user response time, TiDB version, v6.0.0 or earlier versions, Prepared plan cache, Raft-engine, TiKV AsyncIO, TiDB token limit, JDBC, useServerPrepStmts=true, cachePrepStmts=true, prepStmtCacheSize=1000, prepStmtCacheSqlLimit=20480, useConfigs=maxPerformance, StmtPrepare, StmtClose, client-side cache prepared statement objects, PingCAP support team
- Follow-up Guidance: The chunk continues with version checks, TiDB token limit, JDBC prepared statement settings, and client-side caching of prepared statement objects, and it mentions consulting the PingCAP support team for help.
- Classification Note: This is classified as performance for TiDB Cloud because it covers latency diagnosis and throughput-related tuning items outside the cluster, including Prepared plan cache, JDBC configuration, and token limit.

## Official Source Content

### Bottlenecks outside the TiDB cluster

Observe Latency(P80) on the **Overview** tab. If this value is much lower than the P80 value for user response time, you can determine that the main bottleneck might be outside the TiDB cluster. In this case, you can use the following steps to troubleshoot the bottleneck.

1. Check the TiDB version on the left side of the [Overview tab](https://docs.pingcap.com/tidb/stable/tidb-cloud/monitor-tidb-cluster). If it is v6.0.0 or earlier versions, it is recommended to contact the [PingCAP support team](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support) to confirm if the Prepared plan cache, Raft-engine and TiKV AsyncIO features can be enabled. Enabling these features, along with application-side tuning, can significantly improve throughput performance and reduce latency and resource utilization.
2. If necessary, you can increase the TiDB token limit to increase the throughput.
3. If the prepared plan cache feature is enabled, and you use JDBC on the user side, it is recommended to use the following configuration:

    ```
    useServerPrepStmts=true&cachePrepStmts=true& prepStmtCacheSize=1000&prepStmtCacheSqlLimit=20480&useConfigs=maxPerformance
    ```

   If you do not use JDBC and want to take full advantage of the prepared plan cache feature of the current TiDB cluster, you need to cache the prepared statement objects on the client side. You do not need to reset the calls to StmtPrepare and StmtClose. Reduce the number of commands to be called for each query from 3 to 1. It requires some development effort, depending on your performance requirements and the amount of client-side changes. You can consult the [PingCAP support team](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support) for help.
