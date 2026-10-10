# Physical import mode requirements restrictions and component compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-lightning/tidb-lightning-physical-import-mode.md`
- Source Title: `Physical Import Mode`
- Source Heading Path: `Physical Import Mode > Requirements and restrictions | Physical Import Mode > Requirements and restrictions > Environment requirements | Physical Import Mode > Requirements and restrictions > Version requirements | Physical Import Mode > Requirements and restrictions > Limitations | Physical Import Mode > Requirements and restrictions > Tips for using with other components`
- Source Line Ranges: `48-100`
- Source Scope: `self_managed`
- Primary Component: `lightning`
- Related Components: `tidb`, `tikv`, `tiflash`, `ticdc`, `br`
- Topic Tags: `requirements`, `environment`, `versions`, `limitations`, `production-impact`, `parallel-import`, `compatibility`, `backup`, `pitr`, `character-sets`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0941_c6313ff692`
- Source ID: `tidb-docs-8.1:tidb-lightning/tidb-lightning-physical-import-mode.md#requirements-and-restrictions`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f7d39416c10e596481af5d1d4ffea06dec608574ba336e0ea80375e7dc1f8b2a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-physical-import-mode#requirements-and-restrictions
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-lightning/tidb-lightning-physical-import-mode.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving requirements, restrictions, sizing guidance, or compatibility notes for TiDB Lightning physical import mode and its interaction with TiFlash, TiCDC, and BR.
- Retrieval Keywords: Requirements and restrictions, Environment requirements, Version requirements, Limitations, Tips for using with other components, region-concurrency, sorted-kv-dir, TiDB Lightning >= v4.0.3, TiDB >= v4.0.0, fresh CentOS 7, dedicated server, 10Gbps Ethernet, production, latency-sensitive application, Parallel Import, same table, different tables, do not mix the import modes, DDL and DML operations, single table of 10 TiB at most, 10 Lightning instances at most, TiFlash replica, charset=GBK, TiCDC cannot capture, BR snapshot, AWS EBS volume snapshots, log backup, Point-in-Time Recovery, PITR
- Follow-up Guidance: The chunk includes references to Pause scheduling on the table level, Parallel Import, and log backup and PITR documentation for related constraints.
- Classification Note: This is classified as reference because the content lists environment requirements, version requirements, limitations, and component compatibility facts for physical import mode.

## Official Source Content

## Requirements and restrictions
### Environment requirements

**Operating system**:

It is recommended to use fresh CentOS 7 instances. You can deploy a virtual machine either on your local host or in the cloud. Because TiDB Lightning consumes as much CPU resources as needed by default, it is recommended that you deploy it on a dedicated server. If this is not possible, you can deploy it on a single server together with other TiDB components (for example, tikv-server) and then configure `region-concurrency` to limit the CPU usage from TiDB Lightning. Usually, you can configure the size to 75% of the logical CPU.

**Memory and CPU**:

It is recommended that you allocate CPU more than 32 cores and memory greater than 64 GiB to get better performance.

> **Note:**
>
> When you import a large amount of data, one concurrent import may consume about 2 GiB memory. The total memory usage can be `region-concurrency * 2 GiB`. `region-concurrency` is the same as the number of logical CPUs by default. If the memory size (GiB) is less than twice of the CPU or OOM occurs during the import, you can decrease `region-concurrency` to avoid OOM.

**Storage**: The `sorted-kv-dir` configuration item specifies the temporary storage directory for the sorted key-value files. The directory must be empty, and the storage space must be greater than the size of the dataset to be imported. For better import performance, it is recommended to use a directory different from `data-source-dir` and use flash storage and exclusive I/O for the directory.

**Network**: A 10Gbps Ethernet card is recommended.
### Version requirements

- TiDB Lightning >= v4.0.3.
- TiDB >= v4.0.0.
### Limitations

- Do not use the physical import mode to directly import data to TiDB clusters in production. It has severe performance implications. If you need to do so, refer to [Pause scheduling on the table level](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-physical-import-mode-usage#scope-of-pausing-scheduling-during-import).
- If your TiDB cluster has a latency-sensitive application and a low concurrency, it is strongly recommended that you **do not** use the physical import mode to import data into the cluster. This mode might have significant impact on the online application.
- If you want to run multiple TiDB Lightning instances simultaneously to import data into the same TiDB cluster, you can enable [Parallel Import](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-distributed-import) to coordinate the import. If each instance imports data into **different tables**, the Parallel Import option is not required. However, if multiple instances import data into **the same table**, you need to enable Parallel Import to prevent conflicts and ensure data integrity.
- When you use multiple TiDB Lightning to import data to the same target cluster, do not mix the import modes. That is, do not use the physical import mode and the logical import mode at the same time.
- During the process of importing data, do not perform DDL and DML operations in the target table. Otherwise the import will fail or the data will be inconsistent. At the same time, it is not recommended to perform read operations, because the data you read might be inconsistent. You can perform read and write operations after the import operation is completed.
- A single Lightning process can import a single table of 10 TiB at most. Parallel import can use 10 Lightning instances at most.
### Tips for using with other components

- When you use TiDB Lightning with TiFlash, note the following:

    - Whether you have created a TiFlash replica for a table, you can use TiDB Lightning to import data to the table. However, the import might take longer than the normal import. The import time is influenced by the network bandwidth of the server TiDB Lightning is deployed on, the CPU and disk load on the TiFlash node, and the number of TiFlash replicas.

- TiDB Lightning character sets:

    - TiDB Lightning earlier than v5.4.0 cannot import tables of `charset=GBK`.

- When you use TiDB Lightning with TiCDC, note the following:

    - TiCDC cannot capture the data inserted in the physical import mode.

- When you use TiDB Lightning with BR, note the following:

    - When BR backs up snapshots of tables that are being imported by TiDB Lightning, it might result in inconsistent backup data for those tables.
    - When BR backs up data using AWS EBS volume snapshots, TiDB Lightning might fail to import data.
    - Data imported in TiDB Lightning physical import mode does not support [log backup](https://docs.pingcap.com/tidb/stable/br/br-pitr-guide#start-log-backup) and thereby cannot be restored by Point-in-Time Recovery (PITR).
