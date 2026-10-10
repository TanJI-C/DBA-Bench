# Improvements across TiDB, TiKV, TiFlash, BR, and TiCDC

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.5.1.md`
- Source Title: `TiDB 6.5.1 Release Notes`
- Source Heading Path: `TiDB 6.5.1 Release Notes > Improvements`
- Source Line Ranges: `30-72`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `br`, `operator`, `ticdc`, `tidb`, `tiflash`, `tikv`
- Topic Tags: `improvements`, `ipv6`, `kubernetes`, `initialization`, `sql-script`, `memory`, `plan-cache`, `optimizer`, `read-pool`, `resolved-ts`, `startup`, `pitr`, `redo-log`, `object-storage`, `sink-throughput`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0374_a38c9441c5`
- Source ID: `tidb-docs-8.1:releases/release-6.5.1.md#improvements`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d4b22243e4865ad74247b997ed34109e563944996ddbd061c28ba2ce089f5d21`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.5.1#improvements
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.5.1.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 6.5.1 improvement items across TiDB, TiKV, TiFlash, BR, and TiCDC, including IPv6 support, initialization SQL, memory and plan cache behavior, read pool limits, startup, PITR, redo log storage, and sink throughput.
- Retrieval Keywords: TiDB 6.5.1 Improvements, TiDB Operator v1.4.3 IPv6, dual-stack support, TiDB on Kubernetes IPv6 support, initialize-sql-file, --initialize-sql-file, SQL script executed upon TiDB cluster initialization, expired region cache, --proxy-protocol-fallbackable, PROXY protocol fallback mode, Memory Tracker, plan cache warning, out-of-range estimation, less than 1 core, readpool.unified.max-thread-count, resolved-ts.advance-ts-interval, TiFlash startup, PITR, pull-based sink, redo logs GCS-compatible, redo logs Azure-compatible, MQ sink asynchronous mode, MySQL sink asynchronous mode
- Follow-up Guidance: The source includes a link to TiDB on Kubernetes documentation for IPv6 deployment and a documentation link for the initialize-sql-file configuration item.
- Classification Note: This is classified as a release chunk because it lists improvement items introduced in TiDB 6.5.1 across multiple components and tools.

## Official Source Content

## Improvements

+ TiDB

    - Starting from v6.5.1, the TiDB cluster deployed by TiDB Operator v1.4.3 or higher supports IPv6 addresses. This means that TiDB can support a larger address space and bring you better security and network performance.

        - Full support for IPv6 addressing: TiDB supports using IPv6 addresses for all network connections, including client connections, internal communication between nodes, and communication with external systems.
        - Dual-stack support: If you are not ready to fully switch to IPv6 yet, TiDB also supports dual-stack networks. This means that you can use both IPv4 and IPv6 addresses in the same TiDB cluster and choose a network deployment mode that prioritizes IPv6 by configuration.

      For more information on IPv6 deployment, see [TiDB on Kubernetes documentation](https://docs.pingcap.com/tidb-in-kubernetes/stable/configure-a-tidb-cluster#ipv6-support).

    - Support specifying the SQL script executed upon TiDB cluster initialization [#35624](https://github.com/pingcap/tidb/issues/35624) @[morgo](https://github.com/morgo)

        TiDB v6.5.1 adds a new configuration item [`initialize-sql-file`](https://docs.pingcap.com/tidb/v6.5/tidb-configuration-file#initialize-sql-file-new-in-v651). When you start a TiDB cluster for the first time, you can specify the SQL script to be executed by configuring the command line parameter `--initialize-sql-file`. You can use this feature when you need to perform such operations as modifying the value of a system variable, creating a user, or granting privileges. For more information, see [documentation](https://docs.pingcap.com/tidb/v6.5/tidb-configuration-file#initialize-sql-file-new-in-v651).

    - Clear expired region cache regularly to avoid memory leak and performance degradation [#40461](https://github.com/pingcap/tidb/issues/40461) @[sticnarf](https://github.com/sticnarf)
    - Add a new configuration item `--proxy-protocol-fallbackable` to control whether to enable PROXY protocol fallback mode. When this parameter is set to `true`, TiDB accepts PROXY client connections and client connections without any PROXY protocol header [#41409](https://github.com/pingcap/tidb/issues/41409) @[blacktear23](https://github.com/blacktear23)
    - Improve the accuracy of Memory Tracker [#40900](https://github.com/pingcap/tidb/issues/40900) [#40500](https://github.com/pingcap/tidb/issues/40500) @[wshwsh12](https://github.com/wshwsh12)
    - When the plan cache fails to take effect, the system returns the reason as a warning [#40210](https://github.com/pingcap/tidb/pull/40210) @[qw4990](https://github.com/qw4990)
    - Improve the optimizer strategy for out-of-range estimation [#39008](https://github.com/pingcap/tidb/issues/39008) @[time-and-fate](https://github.com/time-and-fate)

+ TiKV

    - Support starting TiKV on a CPU with less than 1 core [#13586](https://github.com/tikv/tikv/issues/13586) [#13752](https://github.com/tikv/tikv/issues/13752) [#14017](https://github.com/tikv/tikv/issues/14017) @[andreid-db](https://github.com/andreid-db)
    - Increase the thread limit of the Unified Read Pool (`readpool.unified.max-thread-count`) to 10 times the CPU quota, to better handle high-concurrency queries [#13690](https://github.com/tikv/tikv/issues/13690) @[v01dstar](https://github.com/v01dstar)
    - Change the default value of `resolved-ts.advance-ts-interval` from `"1s"` to `"20s"`, to reduce cross-region traffic [#14100](https://github.com/tikv/tikv/issues/14100) @[overvenus](https://github.com/overvenus)

+ TiFlash

    - Accelerate TiFlash startup greatly when the data volume is large [#6395](https://github.com/pingcap/tiflash/issues/6395) @[hehechen](https://github.com/hehechen)

+ Tools

    + Backup & Restore (BR)

        - Optimize the concurrency of downloading log backup files on the TiKV side to improve the performance of PITR in regular scenarios [#14206](https://github.com/tikv/tikv/issues/14206) @[YuJuncen](https://github.com/YuJuncen)

    + TiCDC

        - Enable pull-based sink to optimize system throughput [#8232](https://github.com/pingcap/tiflow/issues/8232) @[hi-rustin](https://github.com/Rustin170506)
        - Support storing redo logs to GCS-compatible or Azure-compatible object storage [#7987](https://github.com/pingcap/tiflow/issues/7987) @[CharlesCheung96](https://github.com/CharlesCheung96)
        - Implement MQ sink and MySQL sink in the asynchronous mode to improve the sink throughput [#5928](https://github.com/pingcap/tiflow/issues/5928) @[amyangfei](https://github.com/amyangfei) @[CharlesCheung96](https://github.com/CharlesCheung96)
