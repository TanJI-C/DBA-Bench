# TiDB Binlog Grafana access and monitoring metrics

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-binlog/monitor-tidb-binlog-cluster.md`
- Source Title: `TiDB Binlog Monitoring`
- Source Heading Path: `TiDB Binlog Monitoring | TiDB Binlog Monitoring > Monitoring metrics | TiDB Binlog Monitoring > Monitoring metrics > Pump monitoring metrics | TiDB Binlog Monitoring > Monitoring metrics > Drainer monitoring metrics`
- Source Line Ranges: `5-46`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`
- Topic Tags: `grafana`, `monitoring`, `metrics`, `pump`, `drainer`, `binlog`, `storage`, `latency`, `checkpoint`, `qps`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0085_8c1e54dc40`
- Source ID: `tidb-docs-8.1:tidb-binlog/monitor-tidb-binlog-cluster.md#tidb-binlog-monitoring`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4e5e41bb88e41eadf3711099205b7fc09085b242b003fdb75ab301b34c71573e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-binlog/monitor-tidb-binlog-cluster#tidb-binlog-monitoring
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-binlog/monitor-tidb-binlog-cluster.md

## Retrieval Guidance

- Use When: Use this chunk when you need the Grafana entry point for TiDB Binlog and the names and meanings of Pump and Drainer monitoring metrics.
- Retrieval Keywords: TiDB Binlog Monitoring, Grafana Web, http://grafana_ip:3000, Pump monitoring metrics, Drainer monitoring metrics, Storage Size, Metadata, gc_tso, max_commit_tso, Write Binlog QPS by Instance, Write Binlog Latency, Storage Write Binlog Size, Storage Write Binlog Latency, Pump Storage Error By Type, Query TiKV, Checkpoint TSO, Pump Handle TSO, Pull Binlog QPS by Pump NodeID, 95% Binlog Reach Duration By Pump, Error By Type, SQL Query Time, Drainer Event, Execute Time, 95% Binlog Size, DDL Job Count, Queue Size
- Follow-up Guidance: The source distinguishes Pump metrics such as storage, metadata, write latency, and Query TiKV from Drainer metrics such as Checkpoint TSO, Pump Handle TSO, replication delay, SQL Query Time, and Queue Size.
- Classification Note: This is classified as observability because the content is a Grafana monitoring reference that defines TiDB Binlog metrics for Pump and Drainer.

## Official Source Content

# TiDB Binlog Monitoring

After you have deployed TiDB Binlog successfully, you can go to the Grafana Web (default address: <http://grafana_ip:3000>, default account: admin, password: admin) to check the state of Pump and Drainer.
## Monitoring metrics

TiDB Binlog consists of two components: Pump and Drainer. This section shows the monitoring metrics of Pump and Drainer.
### Pump monitoring metrics

To understand the Pump monitoring metrics, check the following table:

| Pump monitoring metrics | Description |
| --- | --- |
| Storage Size | Records the total disk space (capacity) and the available disk space (available)|
| Metadata | Records the biggest TSO (`gc_tso`) of the binlog that each Pump node can delete, and the biggest commit TSO (`max_commit_tso`) of the saved binlog |
| Write Binlog QPS by Instance | Shows QPS of writing binlog requests received by each Pump node |
| Write Binlog Latency | Records the latency time of each Pump node writing binlog |
| Storage Write Binlog Size | Shows the size of the binlog data written by Pump |
| Storage Write Binlog Latency | Records the latency time of the Pump storage module writing binlog |
| Pump Storage Error By Type | Records the number of errors encountered by Pump, counted based on the type of error |
| Query TiKV | The number of times that Pump queries the transaction status through TiKV |
### Drainer monitoring metrics

To understand the Drainer monitoring metrics, check the following table:

| Drainer monitoring metrics | Description |
| --- | --- |
| Checkpoint TSO | Shows the biggest TSO time of the binlog that Drainer has already replicated into the downstream. You can get the lag by using the current time to subtract the binlog timestamp. But be noted that the timestamp is allocated by PD of the master cluster and is determined by the time of PD.|
| Pump Handle TSO | Records the biggest TSO time among the binlog files that Drainer obtains from each Pump node |
| Pull Binlog QPS by Pump NodeID | Shows the QPS when Drainer obtains binlog from each Pump node |
| 95% Binlog Reach Duration By Pump | Records the delay from the time when binlog is written into Pump to the time when the binlog is obtained by Drainer |
| Error By Type | Shows the number of errors encountered by Drainer, counted based on the type of error |
| SQL Query Time | Records the time it takes Drainer to execute the SQL statement in the downstream |
| Drainer Event | Shows the number of various types of events, including "ddl", "insert", "delete", "update", "flush", and "savepoint" |
| Execute Time | Records the time it takes to write binlog into the downstream syncing module |
| 95% Binlog Size | Shows the size of the binlog data that Drainer obtains from each Pump node |
| DDL Job Count | Records the number of DDL statements handled by Drainer |
| Queue Size | Records the work queue size in Drainer |
