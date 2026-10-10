# Bug fixes for TiKV and PD

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.2.4.md`
- Source Title: `TiDB 5.2.4 Release Notes`
- Source Heading Path: `TiDB 5.2.4 Release Notes > Bug fixes`
- Source Line Ranges: `100-133`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `pd`, `tidb`
- Topic Tags: `bug-fixes`, `panic`, `oom`, `replica-read`, `linearizability`, `region-merge`, `resolved-ts`, `metrics`, `memory-leak`, `flow-control`, `grpc`, `peer-management`, `hotspot`, `scatter`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0249_de1fda0503`
- Source ID: `tidb-docs-8.1:releases/release-5.2.4.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `54b3693a5545d01f4a038cbcc1fb7eca081740fa37db4cd2685fd4a4e26f68b7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.2.4#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.2.4.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 5.2.4 bug fixes in TiKV or PD involving panic, OOM, replica read linearizability, Region merge, Resolved TS, metrics, gRPC latency, snapshots, peers, hotspot statistics, or Region scatterer behavior.
- Retrieval Keywords: TiDB 5.2.4 bug fixes TiKV PD, stale messages cause TiKV to panic, #12023, intermittent packet loss out of memory caused by overflow of memory metrics, #12160, tikv-ctl returns an incorrect result wrong string match, #12329, replica reads might violate the linearizability, #12109, QPS drop flow control level0_slowdown_trigger, #11424, cgroup controller is not mounted panic, #11569, metadata corruption caused by Region merge on a lagging Region peer, #11526, latency of Resolved TS increases after TiKV stops operating, #11351, Region merge ConfChange Snapshot panic, #11475, retrying prewrite requests in the pessimistic transaction mode data inconsistency, #11187, memory leak caused by monitoring data of statistics threads, #11195, average latency of the by-instance gRPC requests is inaccurate, #11299, unsafe_destroy_range GC worker is busy, #11903, reverse table scan memory lock, #11440, destroying a peer might cause high latency, #10210, Region scatterer scheduling lost some peers, #4565, cold hotspot data cannot be deleted from the hotspot statistics, #4390
- Follow-up Guidance: The same Bug fixes section continues with TiFlash fixes and then Tools fixes including Backup & Restore (BR) and TiCDC.
- Classification Note: This chunk is classified as a release note for the TiKV primary component because the official content lists TiDB 5.2.4 bug fixes mainly for TiKV and also includes PD items.

## Official Source Content

- Fix a bug that stale messages cause TiKV to panic [#12023](https://github.com/tikv/tikv/issues/12023)
    - Fix the issue of intermittent packet loss and out of memory (OOM) caused by the overflow of memory metrics [#12160](https://github.com/tikv/tikv/issues/12160)
    - Fix the potential panic issue that occurs when TiKV performs profiling on Ubuntu 18.04 [#9765](https://github.com/tikv/tikv/issues/9765)
    - Fix the issue that tikv-ctl returns an incorrect result due to its wrong string match [#12329](https://github.com/tikv/tikv/issues/12329)
    - Fix a bug that replica reads might violate the linearizability [#12109](https://github.com/tikv/tikv/issues/12109)
    - Fix a bug that TiKV might panic if it has been running for 2 years or more [#11940](https://github.com/tikv/tikv/issues/11940)
    - Fix the issue of QPS drop when flow control is enabled and `level0_slowdown_trigger` is set explicitly [#11424](https://github.com/tikv/tikv/issues/11424)
    - Fix the panic issue that occurs when the cgroup controller is not mounted [#11569](https://github.com/tikv/tikv/issues/11569)
    - Fix possible metadata corruption caused by Region merge on a lagging Region peer [#11526](https://github.com/tikv/tikv/issues/11526)
    - Fix the issue that the latency of Resolved TS increases after TiKV stops operating [#11351](https://github.com/tikv/tikv/issues/11351)
    - Fix a panic issue that occurs when Region merge, ConfChange, and Snapshot happen at the same time in extreme conditions [#11475](https://github.com/tikv/tikv/issues/11475)
    - Fix a bug that tikv-ctl cannot return the correct Region-related information [#11393](https://github.com/tikv/tikv/issues/11393)
    - Fix the issue of negative sign when the decimal divide result is zero [#29586](https://github.com/pingcap/tidb/issues/29586)
    - Fix the issue that retrying prewrite requests in the pessimistic transaction mode might cause the risk of data inconsistency in rare cases [#11187](https://github.com/tikv/tikv/issues/11187)
    - Fix a memory leak caused by monitoring data of statistics threads [#11195](https://github.com/tikv/tikv/issues/11195)
    - Fix the issue that the average latency of the by-instance gRPC requests is inaccurate in TiKV metrics [#11299](https://github.com/tikv/tikv/issues/11299)
    - Fix the panic issue caused by deleting snapshot files when the peer status is `Applying` [#11746](https://github.com/tikv/tikv/issues/11746)
    - Fix a bug that TiKV cannot delete a range of data (which means the internal command `unsafe_destroy_range` is executed) when the GC worker is busy [#11903](https://github.com/tikv/tikv/issues/11903)
    - Fix the issue that deleting an uninitialized replica might cause an old replica to be recreated [#10533](https://github.com/tikv/tikv/issues/10533)
    - Fix the issue that TiKV cannot detect the memory lock when TiKV performs a reverse table scan [#11440](https://github.com/tikv/tikv/issues/11440)
    - Fix the deadlock issue that happens occasionally when coroutines run too fast [#11549](https://github.com/tikv/tikv/issues/11549)
    - Fix the issue that destroying a peer might cause high latency [#10210](https://github.com/tikv/tikv/issues/10210)
    - Fix the issue that TiKV panics and destroys peers unexpectedly because the target Region to be merged is invalid [#12232](https://github.com/tikv/tikv/issues/12232)
    - Fix the TiKV panic issue that occurs when the target peer is replaced with the peer that is destroyed without being initialized when merging a Region [#12048](https://github.com/tikv/tikv/issues/12048)
    - Fix the TiKV panic issue that occurs when applying snapshot is aborted [#11618](https://github.com/tikv/tikv/issues/11618)
    - Fix a bug that TiKV cannot correctly calculate the number of snapshots being sent when the operator execution fails [#11341](https://github.com/tikv/tikv/issues/11341)

+ PD

    - Fix the issue that the Region scatterer scheduling lost some peers [#4565](https://github.com/tikv/pd/issues/4565)
    - Fix the issue that the cold hotspot data cannot be deleted from the hotspot statistics [#4390](https://github.com/tikv/pd/issues/4390)

+ TiFlash
