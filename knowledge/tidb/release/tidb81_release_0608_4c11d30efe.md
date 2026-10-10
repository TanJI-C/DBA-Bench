# Bug fixes for TiKV, PD, and TiFlash

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-8.1.2.md`
- Source Title: `TiDB 8.1.2 Release Notes`
- Source Heading Path: `TiDB 8.1.2 Release Notes > Bug fixes`
- Source Line Ranges: `94-138`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tikv`, `pd`, `tiflash`, `tidb`, `ticdc`
- Topic Tags: `bug fixes`, `stability`, `latency`, `leader election`, `memory leak`, `panic`, `region split`, `resource control`, `replication`, `security`, `sql functions`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0608_4c11d30efe`
- Source ID: `tidb-docs-8.1:releases/release-8.1.2.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `300660cbeb0b258974f806bfa8f1f0e00223dac8d1a49f12b3bfa5ce22182c74`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-8.1.2#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-8.1.2.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 8.1.2 bug fixes in TiKV, PD, or TiFlash related to replication latency, panic, leader election, memory leak, scheduler behavior, SQL function correctness, or region and snapshot handling.
- Retrieval Keywords: TiDB 8.1.2 bug fixes, TiKV resolved-ts.advance-ts-interval, TiCDC replication latency after TiKV restarts, PITR latency increase, TiKV high tail latency resource control, TiKV panic merging Regions, TiKV cannot report heartbeats to PD when disk is stuck, slow disk detection RocksDB different disks, stale replica processes Raft snapshots panic, RADIANS(), DEGREES(), deadlock detection OOM same key lock release, leader quickly elected after Region split, Raft Engine MemTable outdated indexes panic, flow control after deleting large tables or partitions, PD HTTP client retry logic, Gin Web Framework v1.10.0, PD re-elect a leader during etcd leader transition, replication.strictly-match-label, TiFlash fail to start, evict-leader-scheduler same Store ID, performance jitter random number generator, hotspot cache memory leak, label statistics memory leak, deleted resource groups still appear in the monitoring panel, PD leader switched in the microservice mode, wrong parameter in evict-leader-scheduler, resource group selector does not take effect, TiFlash spurious Region overlap check failures, SUBSTRING() negative second parameter, late materialization query errors, Bit-type columns invalid characters, JSON functions unsupported by TiFlash are pushed down, CAST AS DECIMAL sign incorrect, disaggregated storage and compute architecture, read snapshots of TiFlash write nodes not released, SUBSTRING() pos len integer types, CAST() string to datetime with a time zone, LPAD(), RPAD(), querying new columns incorrect results
- Follow-up Guidance: 
- Classification Note: This chunk is classified as a release note bug-fix summary covering self-managed TiDB 8.1.2 fixes across TiKV, PD, TiFlash, and one TiDB indexing fix.

## Official Source Content

- Fix the issue that the index timestamp is set to `0` when adding indexes to large tables in a non-distributed manner [#57980](https://github.com/pingcap/tidb/issues/57980) @[lance6716](https://github.com/lance6716)

+ TiKV

    - Fix the issue that the configuration `resolved-ts.advance-ts-interval` does not take effect, causing the replication latency of TiCDC and Point-in-time recovery (PITR) to increase dramatically when TiKV restarts [#17107](https://github.com/tikv/tikv/issues/17107) @[MyonKeminta](https://github.com/MyonKeminta)
    - Fix the issue that some tasks experience high tail latency when triggering resource control [#17589](https://github.com/tikv/tikv/issues/17589) @[glorv](https://github.com/glorv)
    - Fix the issue that merging Regions might cause TiKV to panic in rare cases [#17840](https://github.com/tikv/tikv/issues/17840) @[glorv](https://github.com/glorv)
    - Fix the issue that TiKV cannot report heartbeats to PD when the disk is stuck [#17939](https://github.com/tikv/tikv/issues/17939) @[LykxSassinator](https://github.com/LykxSassinator)
    - Fix the issue that when Raft and RocksDB are deployed on different disks, the slow disk detection does not work for the disk where RocksDB is located [#17884](https://github.com/tikv/tikv/issues/17884) @[LykxSassinator](https://github.com/LykxSassinator)
    - Fix the issue that TiKV might panic when a stale replica processes Raft snapshots, triggered by a slow split operation and immediate removal of the new replica [#17469](https://github.com/tikv/tikv/issues/17469) @[hbisheng](https://github.com/hbisheng)
    - Fix the issue that TiKV might panic when executing queries containing `RADIANS()` or `DEGREES()` functions [#17852](https://github.com/tikv/tikv/issues/17852) @[gengliqi](https://github.com/gengliqi)
    - Fix the issue that when a large number of transactions are queuing for lock release on the same key and the key is frequently updated, excessive pressure on deadlock detection might cause TiKV OOM issues [#17394](https://github.com/tikv/tikv/issues/17394) @[MyonKeminta](https://github.com/MyonKeminta)
    - Fix the issue that the leader could not be quickly elected after Region split [#17602](https://github.com/tikv/tikv/issues/17602) @[LykxSassinator](https://github.com/LykxSassinator)
    - Fix the panic issue that occurs when read threads access outdated indexes in the MemTable of the Raft Engine [#17383](https://github.com/tikv/tikv/issues/17383) @[LykxSassinator](https://github.com/LykxSassinator)
    - Fix the flow control issue that might occur after deleting large tables or partitions [#17304](https://github.com/tikv/tikv/issues/17304) @[Connor1996](https://github.com/Connor1996)

+ PD

    - Fix the issue that the PD HTTP client retry logic might be ineffective [#8499](https://github.com/tikv/pd/issues/8499) @[JmPotato](https://github.com/JmPotato)
    - Upgrade the version of Gin Web Framework from v1.9.1 to v1.10.0 to fix potential security vulnerabilities [#8643](https://github.com/tikv/pd/issues/8643) @[JmPotato](https://github.com/JmPotato)
    - Fix the issue that PD cannot quickly re-elect a leader during etcd leader transition [#8823](https://github.com/tikv/pd/issues/8823) @[rleungx](https://github.com/rleungx)
    - Fix the issue that setting `replication.strictly-match-label` to `true` causes TiFlash to fail to start [#8480](https://github.com/tikv/pd/issues/8480) @[rleungx](https://github.com/rleungx)
    - Fix the issue that `evict-leader-scheduler` fails to work properly when it is repeatedly created with the same Store ID [#8756](https://github.com/tikv/pd/issues/8756) @[okJiang](https://github.com/okJiang)
    - Fix the performance jitter issue caused by frequent creation of random number generator [#8674](https://github.com/tikv/pd/issues/8674) @[rleungx](https://github.com/rleungx)
    - Fix the memory leak issue in hotspot cache [#8698](https://github.com/tikv/pd/issues/8698) @[lhy1024](https://github.com/lhy1024)
    - Fix the memory leak issue in label statistics [#8700](https://github.com/tikv/pd/issues/8700) @[lhy1024](https://github.com/lhy1024)
    - Fix the issue that deleted resource groups still appear in the monitoring panel [#8716](https://github.com/tikv/pd/issues/8716) @[AndreMouche](https://github.com/AndreMouche)
    - Fix the issue that data race might occur in the scheduling server when a PD leader is switched in the microservice mode [#8538](https://github.com/tikv/pd/issues/8538) @[lhy1024](https://github.com/lhy1024)
    - Fix the issue that when using a wrong parameter in `evict-leader-scheduler`, PD does not report errors correctly and some schedulers are unavailable [#8619](https://github.com/tikv/pd/issues/8619) @[rleungx](https://github.com/rleungx)
    - Fix the issue that the resource group selector does not take effect on any panel [#56572](https://github.com/pingcap/tidb/issues/56572) @[glorv](https://github.com/glorv)

+ TiFlash

    - Fix the issue that TiFlash might panic due to spurious Region overlap check failures that occur when multiple Regions are concurrently applying snapshots [#9329](https://github.com/pingcap/tiflash/issues/9329) @[CalvinNeo](https://github.com/CalvinNeo)
    - Fix the issue that the `SUBSTRING()` function returns incorrect results when the second parameter is negative [#9604](https://github.com/pingcap/tiflash/issues/9604) @[guo-shaoge](https://github.com/guo-shaoge)
    - Fix the issue that some queries might report errors when late materialization is enabled [#9472](https://github.com/pingcap/tiflash/issues/9472) @[Lloyd-Pottiger](https://github.com/Lloyd-Pottiger)
    - Fix the issue that TiFlash fails to parse the table schema when the table contains Bit-type columns with a default value that contains invalid characters [#9461](https://github.com/pingcap/tiflash/issues/9461) @[Lloyd-Pottiger](https://github.com/Lloyd-Pottiger)
    - Fix the issue that some JSON functions unsupported by TiFlash are pushed down to TiFlash [#9444](https://github.com/pingcap/tiflash/issues/9444) @[windtalker](https://github.com/windtalker)
    - Fix the issue that the sign in the result of the `CAST AS DECIMAL` function is incorrect in certain cases [#9301](https://github.com/pingcap/tiflash/issues/9301) @[guo-shaoge](https://github.com/guo-shaoge)
    - Fix the issue that read snapshots of TiFlash write nodes are not released in a timely manner in the disaggregated storage and compute architecture [#9298](https://github.com/pingcap/tiflash/issues/9298) @[JinheLin](https://github.com/JinheLin)
    - Fix the issue that the `SUBSTRING()` function does not support the `pos` and `len` arguments for certain integer types, causing query errors [#9473](https://github.com/pingcap/tiflash/issues/9473) @[gengliqi](https://github.com/gengliqi)
    - Fix the issue that when using the `CAST()` function to convert a string to a datetime with a time zone or invalid characters, the result is incorrect [#8754](https://github.com/pingcap/tiflash/issues/8754) @[solotzg](https://github.com/solotzg)
    - Fix the issue that `LPAD()` and `RPAD()` functions return incorrect results in some cases [#9465](https://github.com/pingcap/tiflash/issues/9465) @[guo-shaoge](https://github.com/guo-shaoge)
    - Fix the issue that querying new columns might return incorrect results under the disaggregated storage and compute architecture [#9665](https://github.com/pingcap/tiflash/issues/9665) @[zimulala](https://github.com/zimulala)
