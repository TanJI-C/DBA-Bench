# Replication performance, recovery cautions, deployment, and execution behavior

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-faq.md`
- Source Title: `TiCDC FAQs`
- Source Heading Path: `TiCDC FAQs > Why does TiCDC use disks? When does TiCDC write to disks? Does TiCDC use memory buffer to improve replication performance? | TiCDC FAQs > Why does replication using TiCDC stall or even stop after data restore using TiDB Lightning physical import mode and BR from upstream? | TiCDC FAQs > After a changefeed resumes from pause, its replication latency gets higher and higher and returns to normal only after a few minutes. Why? | TiCDC FAQs > How should I deploy TiCDC to replicate data between two TiDB cluster located in different regions? | TiCDC FAQs > What is the order of executing DML and DDL statements? | TiCDC FAQs > How should I check whether the upstream and downstream data is consistent? | TiCDC FAQs > Replication of a single table can only be run on a single TiCDC node. Will it be possible to use multiple TiCDC nodes to replicate data of multiple tables? | TiCDC FAQs > Does TiCDC replication get stuck if the upstream has long-running uncommitted transactions?`
- Source Line Ranges: `368-420`
- Source Scope: `shared`
- Primary Component: `ticdc`
- Related Components: `br`, `lightning`, `pd`, `tikv`
- Topic Tags: `disk-usage`, `backpressure`, `restore-compatibility`, `data-loss-warning`, `pause-resume`, `cross-region-deployment`, `ddl-ordering`, `data-consistency`, `mq-sink`, `table-across-nodes`, `long-transactions`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0253_d44f2d953d`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-faq.md#why-does-ticdc-use-disks-when-does-ticdc-write-to-disks-does-ticdc-use-memory-buffer-to-improve-replication-performance`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `93c064fea39bbf3473063bb4bddd21b0ebf926e293301962dda5fdc4abab3da4`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-faq#why-does-ticdc-use-disks-when-does-ticdc-write-to-disks-does-ticdc-use-memory-buffer-to-improve-replication-performance
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-faq.md

## Retrieval Guidance

- Use When: Use this chunk when troubleshooting TiCDC disk usage, restore-related replication stalls, pause-resume catch-up latency, cross-region deployment placement, DDL and DML execution order, consistency checking, MQ sink table-across-nodes support, or delays from long-running uncommitted transactions.
- Retrieval Keywords: TiCDC use disks, data pile-up, memory buffer, TiDB Lightning physical import mode, BR, replication getting stuck, significant spike in replication latency, data loss, remove the TiCDC replication task, start-ts, cdc cli changefeed create, 431434047157698561, changefeed resumes from pause, scan historical versions of data in TiKV, different regions, more than 100 ms, deploy TiCDC in the downstream TiDB cluster, starting from TiCDC v6.5.2 deploy TiCDC in the upstream TiDB cluster, DDL commitTS, serial manner, sync-diff-inspector, MQ sink, TiKV Regions, enable-table-across-nodes = true, max-txn-ttl, long-running uncommitted transactions
- Follow-up Guidance: The content includes a restore-related sequence with removing the TiCDC replication task, restoring data separately in upstream and downstream, verifying consistency, and creating a new changefeed with the upstream backup timestamp as `start-ts`.
- Classification Note: This is classified as operation because the official content covers runtime behavior, deployment placement, recovery cautions, consistency verification, scaling configuration, and replication delay scenarios.

## Official Source Content

## Why does TiCDC use disks? When does TiCDC write to disks? Does TiCDC use memory buffer to improve replication performance?

When upstream write traffic is at peak hours, the downstream may fail to consume all data in a timely manner, resulting in data pile-up. TiCDC uses disks to process the data that is piled up. TiCDC needs to write data to disks during normal operation. However, this is not usually the bottleneck for replication throughput and replication latency, given that writing to disks only results in latency within a hundred milliseconds. TiCDC also uses memory to accelerate reading data from disks to improve replication performance.
## Why does replication using TiCDC stall or even stop after data restore using TiDB Lightning physical import mode and BR from upstream?

Currently, TiCDC is not yet fully compatible with [TiDB Lightning physical import mode](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-physical-import-mode) and BR. Therefore, avoid using TiDB Lightning physical import mode and BR on tables that are replicated by TiCDC. Otherwise, unknown errors might occur, such as TiCDC replication getting stuck, a significant spike in replication latency, or data loss.

If you need to use TiDB Lightning physical import mode or BR to restore data for some tables replicated by TiCDC, take these steps:

1. Remove the TiCDC replication task related to these tables.

2. Use TiDB Lightning physical import mode or BR to restore data separately in the upstream and downstream clusters of TiCDC.

3. After the restoration is complete and data consistency between the upstream and downstream clusters is verified, create a new TiCDC replication task for incremental replication, with the timestamp (TSO) from the upstream backup as the `start-ts` for the task. For example, assuming the snapshot timestamp of the BR backup in the upstream cluster is `431434047157698561`, you can create a new TiCDC replication task using the following command:

    ```shell
    cdc cli changefeed create -c "upstream-to-downstream-some-tables" --start-ts=431434047157698561 --sink-uri="mysql://root@127.0.0.1:4000? time-zone="
    ```
## After a changefeed resumes from pause, its replication latency gets higher and higher and returns to normal only after a few minutes. Why?

When a changefeed is resumed, TiCDC needs to scan the historical versions of data in TiKV to catch up with the incremental data logs generated during the pause. The replication process proceeds only after the scan is completed. The scan process might take several to tens of minutes.
## How should I deploy TiCDC to replicate data between two TiDB cluster located in different regions?

For TiCDC versions earlier than v6.5.2, it is recommended that you deploy TiCDC in the downstream TiDB cluster. If the network latency between the upstream and downstream is high, for example, more than 100 ms, the latency produced when TiCDC executes SQL statements to the downstream might increase dramatically due to the MySQL transmission protocol issues. This results in a decrease in system throughput. However, deploying TiCDC in the downstream can greatly ease this problem. After optimization, starting from TiCDC v6.5.2, it is recommended that you deploy TiCDC in the upstream TiDB cluster.
## What is the order of executing DML and DDL statements?

Currently, TiCDC adopts the following order:

1. TiCDC blocks the replication progress of the tables affected by DDL statements until the DDL `commitTS`. This ensures that DML statements executed before DDL `commitTS` can be successfully replicated to the downstream first.
2. TiCDC continues with the replication of DDL statements. If there are multiple DDL statements, TiCDC replicates them in a serial manner.
3. After the DDL statements are executed in the downstream, TiCDC will continue with the replication of DML statements executed after DDL `commitTS`.
## How should I check whether the upstream and downstream data is consistent?

If the downstream is a TiDB cluster or MySQL instance, it is recommended that you compare the data using [sync-diff-inspector](https://docs.pingcap.com/tidb/stable/sync-diff-inspector/sync-diff-inspector-overview).
## Replication of a single table can only be run on a single TiCDC node. Will it be possible to use multiple TiCDC nodes to replicate data of multiple tables?

Starting from v7.1.0, TiCDC supports the MQ sink to replicate data change logs at the granularity of TiKV Regions, which achieves scalable processing capability and allows TiCDC to replicate a single table with a large number of Regions. To enable this feature, you can configure the following parameter in the [TiCDC configuration file](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config):

```toml
[scheduler]
enable-table-across-nodes = true
```
## Does TiCDC replication get stuck if the upstream has long-running uncommitted transactions?

TiDB has a transaction timeout mechanism. When a transaction runs for a period longer than [`max-txn-ttl`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#max-txn-ttl), TiDB forcibly rolls it back. TiCDC waits for the transaction to be committed before proceeding with the replication, which causes replication delay.
