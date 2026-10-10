# Pessimistic lock acceleration features and disabling methods

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/pessimistic-transaction.md`
- Source Title: `TiDB Pessimistic Transaction Mode`
- Source Heading Path: `TiDB Pessimistic Transaction Mode > Pipelined locking process | TiDB Pessimistic Transaction Mode > In-memory pessimistic lock`
- Source Line Ranges: `157-219`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `tidb`, `sql`
- Topic Tags: `pessimistic-transactions`, `locking`, `pipelined-locking`, `in-memory-locks`, `latency`, `throughput`, `dynamic-configuration`, `failure-handling`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0137_1363d4746b`
- Source ID: `tidb-docs-8.1:pessimistic-transaction.md#pipelined-locking-process`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ecd18ae1d2d1f0b7e9d121735e626d16e95e68c74b5551a9fb3897ebaa034a67`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/pessimistic-transaction#pipelined-locking-process
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/pessimistic-transaction.md

## Retrieval Guidance

- Use When: Use this chunk when the query is about pipelined locking or in-memory pessimistic lock behavior, their default enabled state, failure impact during TiKV anomalies, or how to disable these TiKV pessimistic transaction acceleration features.
- Retrieval Keywords: pipelined locking process, in-memory pessimistic lock, [pessimistic-txn], pessimistic-txn.pipelined, pessimistic-txn.in-memory, pipelined = false, in-memory = false, set config tikv pessimistic-txn.pipelined='false';, set config tikv pessimistic-txn.in-memory='false';, network partition occurs in TiKV, network isolation occurs in TiKV, TiKV node is down, lock waiting mechanisms, success rate of transaction commits, enabled by default
- Follow-up Guidance: The content also states that when in-memory pessimistic lock memory usage exceeds the threshold, lock acquisition turns to the pipelined locking process, and when a Region is merged or the leader is transferred, TiKV writes the in-memory pessimistic lock to disk and replicates it to other replicas.
- Classification Note: This is classified as configuration because the official content focuses on TiKV settings and dynamic configuration statements that enable or disable pessimistic transaction acceleration features and describes their operational effects.

## Official Source Content

## Pipelined locking process

Adding a pessimistic lock requires writing data into TiKV. The response of successfully adding a lock can only be returned to TiDB after commit and apply through Raft. Therefore, compared with optimistic transactions, the pessimistic transaction mode inevitably has higher latency.

To reduce the overhead of locking, TiKV implements the pipelined locking process: when the data meets the requirements for locking, TiKV immediately notifies TiDB to execute subsequent requests and writes into the pessimistic lock asynchronously. This process reduces most latency and significantly improves the performance of pessimistic transactions. However, when network partition occurs in TiKV or a TiKV node is down, the asynchronous write into the pessimistic lock might fail and affect the following aspects:

* Other transactions that modify the same data cannot be blocked. If the application logic relies on locking or lock waiting mechanisms, the correctness of the application logic is affected.

* There is a low probability that the transaction commit fails, but it does not affect the correctness of the transactions.

If the application logic relies on the locking or lock waiting mechanisms, or if you want to guarantee as much as possible the success rate of transaction commits even in the case of TiKV cluster anomalies, you should disable the pipelined locking feature.

![Pipelined pessimistic lock](/media/pessimistic-transaction-pipelining.png)

This feature is enabled by default. To disable it, modify the TiKV configuration:

```toml
[pessimistic-txn]
pipelined = false
```

If the TiKV cluster is v4.0.9 or later, you can also dynamically disable this feature by [modifying TiKV configuration dynamically](https://docs.pingcap.com/tidb/stable/dynamic-config#modify-tikv-configuration-dynamically):

```sql
set config tikv pessimistic-txn.pipelined='false';
```

If the application logic relies on the locking or lock waiting mechanisms, or if you want to guarantee as much as possible the success rate of transaction commits even in the case of TiKV cluster anomalies, you can [contact TiDB Cloud Support](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support) to disable the pipelined locking feature.
## In-memory pessimistic lock

In v6.0.0, TiKV introduces the feature of in-memory pessimistic lock. When this feature is enabled, pessimistic locks are usually stored in the memory of the Region leader only, and are not persisted to disk or replicated through Raft to other replicas. This feature can greatly reduce the overhead of acquiring pessimistic locks and improve the throughput of pessimistic transactions.

When the memory usage of in-memory pessimistic locks exceeds the memory threshold of the Region or the TiKV node, the acquisition of pessimistic locks turns to the [pipelined locking process](#pipelined-locking-process). When the Region is merged or the leader is transferred, to avoid the loss of the pessimistic lock, TiKV writes the in-memory pessimistic lock to disk and replicates it to other replicas.

The in-memory pessimistic lock performs similarly to the pipelined locking process, which does not affect the lock acquisition when the cluster is healthy. However, when network isolation occurs in TiKV or a TiKV node is down, the acquired pessimistic lock might be lost.

If the application logic relies on the lock acquiring or lock waiting mechanism, or if you want to guarantee as much as possible the success rate of transaction commits even when the cluster is in an abnormal state, you need to **disable** the in-memory pessimistic lock feature.

This feature is enabled by default. To disable it, modify the TiKV configuration:

```toml
[pessimistic-txn]
in-memory = false
```

To dynamically disable this feature, modify the TiKV configuration dynamically:

```sql
set config tikv pessimistic-txn.in-memory='false';
```
