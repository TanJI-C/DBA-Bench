# TiKV server management FAQs: storage behavior, failures, durability, and limits

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/faq/manage-cluster-faq.md`
- Source Title: `TiDB Cluster Management FAQs`
- Source Heading Path: `TiDB Cluster Management FAQs > TiKV server management > The `duplicated store address` message is displayed when starting TiKV | TiDB Cluster Management FAQs > TiKV server management > TiKV primary node and secondary node use the same compression algorithm, why the results are different? | TiDB Cluster Management FAQs > TiKV server management > What are the features of TiKV block cache? | TiDB Cluster Management FAQs > TiKV server management > Why is the TiKV channel full? | TiDB Cluster Management FAQs > TiKV server management > Why does TiKV frequently switch Region leader? | TiDB Cluster Management FAQs > TiKV server management > If a node is down, will the service be affected? If yes, how long? | TiDB Cluster Management FAQs > TiKV server management > What are the TiKV scenarios that take up high I/O, memory, CPU, and exceed the parameter configuration? | TiDB Cluster Management FAQs > TiKV server management > Does TiKV support SAS/SATA disks or mixed deployment of SSD/SAS disks? | TiDB Cluster Management FAQs > TiKV server management > Is the Range of the Key data table divided before data access? | TiDB Cluster Management FAQs > TiKV server management > How does Region split? | TiDB Cluster Management FAQs > TiKV server management > Does TiKV have the `innodb_flush_log_trx_commit` parameter like MySQL, to guarantee the security of data? | TiDB Cluster Management FAQs > TiKV server management > What is the recommended server configuration for WAL storage, such as SSD, RAID level, cache strategy of RAID card, NUMA configuration, file system, I/O scheduling strategy of the operating system? | TiDB Cluster Management FAQs > TiKV server management > How is the write performance in the most strict data available mode (`sync-log = true`)? | TiDB Cluster Management FAQs > TiKV server management > Can Raft + multiple replicas in the TiKV architecture achieve absolute data safety? Is it necessary to apply the most strict mode (`sync-log = true`) to a standalone storage? | TiDB Cluster Management FAQs > TiKV server management > Since TiKV uses the Raft protocol, multiple network roundtrips occur during data writing. What is the actual write delay? | TiDB Cluster Management FAQs > TiKV server management > Does TiDB have an InnoDB memcached plugin like MySQL which can directly use the KV interface and does not need the independent cache? | TiDB Cluster Management FAQs > TiKV server management > What is the Coprocessor component used for? | TiDB Cluster Management FAQs > TiKV server management > The error message `IO error: No space left on device While appending to file` is displayed | TiDB Cluster Management FAQs > TiKV server management > Why does the OOM (Out of Memory) error occur frequently in TiKV? | TiDB Cluster Management FAQs > TiKV server management > Can both TiDB data and RawKV data be stored in the same TiKV cluster?`
- Source Line Ranges: `319-422`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `pd`, `tidb`
- Topic Tags: `store-registration`, `compression`, `block-cache`, `channel-full`, `region-leader`, `node-failure`, `resource-usage`, `disk-requirements`, `region-split`, `sync-log`, `wal`, `raft`, `write-latency`, `coprocessor`, `disk-space`, `oom`, `rawkv`, `api-v2`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0147_0650b87cfd`
- Source ID: `tidb-docs-8.1:faq/manage-cluster-faq.md#the-duplicated-store-address-message-is-displayed-when-starting-tikv`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ae8f00a1d40de0ea00c2c2e229b109aa17fe1df23d08c0deabf6699063134c47`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/faq/manage-cluster-faq#the-duplicated-store-address-message-is-displayed-when-starting-tikv
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/faq/manage-cluster-faq.md

## Retrieval Guidance

- Use When: Use this chunk when troubleshooting TiKV operational FAQs about duplicated store address, block cache and OOM, Region leader switching or split behavior, sync-log durability, WAL configuration, channel full, disk space errors, or RawKV compatibility in the same TiKV cluster.
- Retrieval Keywords: duplicated store address, --data-dir, pd-ctl store delete, block-cache-size, write-buffer-size, rocksdb.defaultcf, rocksdb.writecf, raftdb.defaultcf, TiKV channel full, Raftstore thread, Region leader switch, 2 * lease time, lease time is 10 seconds, region-max-size, region-max-keys, sync-log, innodb_flush_log_trx_commit, raft-log, WAL, RAID 10, interleave = all, ext4, write delay 4 more network roundtrips, Coprocessor, IO error: No space left on device While appending to file, OOM, storage.api-version = 2, TiKV API V2, RawKV
- Follow-up Guidance: The chunk includes related follow-up details such as pd-ctl store delete for duplicated store address, block-cache-size checks for OOM, and the TiKV API V2 condition for storing TiDB data and RawKV data in the same cluster.
- Classification Note: This is classified as TiKV self-managed operation content because the official content focuses on TiKV server behavior, configuration parameters, failure symptoms, durability, storage layout, and resource usage.

## Official Source Content

### The `duplicated store address` message is displayed when starting TiKV

This is because the address in the startup parameter has been registered in the PD cluster by other TiKVs. Common conditions that cause this error: There is no data folder in the path specified by TiKV `--data-dir` (no update --data-dir after deleting or moving), restart the TiKV with the previous parameters.Please try [store delete](https://github.com/pingcap/pd/tree/55db505e8f35e8ab4e00efd202beb27a8ecc40fb/tools/pd-ctl#store-delete--label--weight-store_id----jqquery-string) function of pd-ctl, delete the previous store, and then restart TiKV.
### TiKV primary node and secondary node use the same compression algorithm, why the results are different?

Currently, some files of TiKV primary node have a higher compression rate, which depends on the underlying data distribution and RocksDB implementation. It is normal that the data size fluctuates occasionally. The underlying storage engine adjusts data as needed.
### What are the features of TiKV block cache?

TiKV implements the Column Family (CF) feature of RocksDB. By default, the KV data is eventually stored in the 3 CFs (default, write and lock) within RocksDB.

- The default CF stores real data and the corresponding parameter is in `[rocksdb.defaultcf]`.
- The write CF stores the data version information (MVCC) and index-related data, and the corresponding parameter is in `[rocksdb.writecf]`.
- The lock CF stores the lock information and the system uses the default parameter.
- The Raft RocksDB instance stores Raft logs. The default CF mainly stores Raft logs and the corresponding parameter is in `[raftdb.defaultcf]`.
- All CFs have a shared block-cache to cache data blocks and improve RocksDB read speed. The size of block-cache is controlled by the `block-cache-size` parameter. A larger value of the parameter means more hot data can be cached and is more favorable to read operation. At the same time, it consumes more system memory.
- Each CF has an individual write-buffer and the size is controlled by the `write-buffer-size` parameter.
### Why is the TiKV channel full?

- The Raftstore thread is too slow or blocked by I/O. You can view the CPU usage status of Raftstore.
- TiKV is too busy (such as CPU and disk I/O) and cannot manage to handle it.
### Why does TiKV frequently switch Region leader?

- Network problem results in the communication stuck among nodes. You can check Report failures monitoring.
- The node of the original main Leader is stuck, resulting in failure to reach out to the Follower in time.
- Raftstore thread stuck.
### If a node is down, will the service be affected? If yes, how long?

TiKV uses Raft to replicate data among multiple replicas (by default 3 replicas for each Region). If one replica goes wrong, the other replicas can guarantee data safety. Based on the Raft protocol, if a single leader fails as the node goes down, a follower in another node is soon elected as the Region leader after a maximum of 2 * lease time (lease time is 10 seconds).
### What are the TiKV scenarios that take up high I/O, memory, CPU, and exceed the parameter configuration?

Writing or reading a large volume of data in TiKV takes up high I/O, memory and CPU. Executing very complex queries costs a lot of memory and CPU resources, such as the scenario that generates large intermediate result sets.
### Does TiKV support SAS/SATA disks or mixed deployment of SSD/SAS disks?

No. For OLTP scenarios, TiDB requires high I/O disks for data access and operation. As a distributed database with strong consistency, TiDB has some write amplification such as replica replication and bottom layer storage compaction. Therefore, it is recommended to use NVMe SSD as the storage disks in TiDB best practices. Mixed deployment of TiKV and PD is not supported.
### Is the Range of the Key data table divided before data access?

No. It differs from the table splitting rules of MySQL. In TiKV, the table Range is dynamically split based on the size of Region.
### How does Region split?

Region is not divided in advance, but it follows a Region split mechanism. When the Region size exceeds the value of the `region-max-size` or `region-max-keys` parameters, split is triggered. After the split, the information is reported to PD.
### Does TiKV have the `innodb_flush_log_trx_commit` parameter like MySQL, to guarantee the security of data?

Yes. Currently, the standalone storage engine uses two RocksDB instances. One instance is used to store the raft-log. When the `sync-log` parameter in TiKV is set to true, each commit is mandatorily flushed to the raft-log. If a crash occurs, you can restore the KV data using the raft-log.
### What is the recommended server configuration for WAL storage, such as SSD, RAID level, cache strategy of RAID card, NUMA configuration, file system, I/O scheduling strategy of the operating system?

WAL belongs to ordered writing, and currently, we do not apply a unique configuration to it. Recommended configuration is as follows:

- SSD
- RAID 10 preferred
- Cache strategy of RAID card and I/O scheduling strategy of the operating system: currently no specific best practices; you can use the default configuration in Linux 7 or later
- NUMA: no specific suggestion; for memory allocation strategy, you can use `interleave = all`
- File system: ext4
### How is the write performance in the most strict data available mode (`sync-log = true`)?

Generally, enabling `sync-log` reduces about 30% of the performance. For write performance when `sync-log` is set to `false`, see [Performance test result for TiDB using Sysbench](https://docs.pingcap.com/tidb/stable/benchmark/v3.0-performance-benchmarking-with-sysbench).
### Can Raft + multiple replicas in the TiKV architecture achieve absolute data safety? Is it necessary to apply the most strict mode (`sync-log = true`) to a standalone storage?

Data is redundantly replicated between TiKV nodes using the [Raft Consensus Algorithm](https://raft.github.io/) to ensure recoverability should a node failure occur. Only when the data has been written into more than 50% of the replicas will the application return ACK (two out of three nodes). However, theoretically, two nodes might crash. Therefore, except for scenarios with less strict requirement on data safety but extreme requirement on performance, it is strongly recommended that you enable the `sync-log` mode.

As an alternative to using `sync-log`, you may also consider having five replicas instead of three in your Raft group. This would allow for the failure of two replicas, while still providing data safety.

For a standalone TiKV node, it is still recommended to enable the `sync-log` mode. Otherwise, the last write might be lost in case of a node failure.
### Since TiKV uses the Raft protocol, multiple network roundtrips occur during data writing. What is the actual write delay?

Theoretically, TiDB has a write delay of 4 more network roundtrips than standalone databases.
### Does TiDB have an InnoDB memcached plugin like MySQL which can directly use the KV interface and does not need the independent cache?

TiKV supports calling the interface separately. Theoretically, you can take an instance as the cache. Because TiDB is a distributed relational database, we do not support TiKV separately.
### What is the Coprocessor component used for?

- Reduce the data transmission between TiDB and TiKV
- Make full use of the distributed computing resources of TiKV to execute computing pushdown.
### The error message `IO error: No space left on device While appending to file` is displayed

This is because the disk space is not enough. You need to add nodes or enlarge the disk space.
### Why does the OOM (Out of Memory) error occur frequently in TiKV?

The memory usage of TiKV mainly comes from the block-cache of RocksDB, which is 40% of the system memory size by default. When the OOM error occurs frequently in TiKV, you should check whether the value of `block-cache-size` is set too high. In addition, when multiple TiKV instances are deployed on a single machine, you need to explicitly configure the parameter to prevent multiple instances from using too much system memory that results in the OOM error.
### Can both TiDB data and RawKV data be stored in the same TiKV cluster?

It depends on your TiDB version and whether TiKV API V2 is enabled ([`storage.api-version = 2`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#api-version-new-in-v610)). 

- If your TiDB version is v6.1.0 or later and TiKV API V2 is enabled, TiDB data and RawKV data can be stored in the same TiKV cluster. 
- Otherwise, the answer is no because the key format of TiDB data (or data created using the transactional API) is incompatible with data created using the RawKV API (or data from other RawKV-based services).
