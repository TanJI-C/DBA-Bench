# TiDB 2.1 GA PD enhancements

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-2.1-ga.md`
- Source Title: `TiDB 2.1 GA Release Notes`
- Source Heading Path: `TiDB 2.1 GA Release Notes > Placement Driver (PD)`
- Source Line Ranges: `136-204`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: `tikv`, `tidb`, `shared`
- Topic Tags: `release-notes`, `availability`, `rolling-update`, `raft-prevote`, `raft-learner`, `region-merge`, `scheduler`, `pd-ctl`, `api`, `metrics`, `performance`, `gc-safepoint`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0041_c781ae4714`
- Source ID: `tidb-docs-8.1:releases/release-2.1-ga.md#placement-driver-pd`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `776c220e92caeac4b6cc18d6655c5d68f6fde20656c92e950ad7fc79ef82b1e5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-2.1-ga#placement-driver-pd
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-2.1-ga.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 2.1 GA release-note details about PD availability, scheduler, API, pd-ctl, metrics, and performance enhancements.
- Retrieval Keywords: TiDB 2.1 GA Release Notes, Placement Driver (PD), PD 2.1 GA, rolling update, version control mechanism, Raft PreVote, raft learner, TSO allocation, Region merge, scheduler, Down Store, hotspot scheduler, Coordinator, Balance Scheduler, pd-ctl, GetPrevRegion, BatchSplitRegion, GCSafePoint, GetAllStores, PD simulator, jq formatted JSON output, region store store_id, region topconfver, region topsize, TSO encoding, pd-recover, max-replica, Filter metrics, etcd Raft state machine, Region heartbeat, Region tree, hotspot statistics
- Follow-up Guidance: The source includes linked references for `Raft PreVote`, pd-ctl commands, `pd-recover`, and PD interfaces such as `GetPrevRegion`, `BatchSplitRegion`, `GCSafePoint`, and `GetAllStores`.
- Classification Note: This chunk is classified under the PD component because the official content summarizes PD-specific 2.1 GA changes in availability, scheduling, APIs and tools, metrics, and performance.

## Official Source Content

## Placement Driver (PD)

+ Optimize availability

    - Introduce the version control mechanism and support rolling update of the cluster compatibly

    - [Enable `Raft PreVote`](https://github.com/pingcap/pd/blob/5c7b18cf3af91098f07cf46df0b59fbf8c7c5462/conf/config.toml#L22) among PD nodes to avoid leader reelection when network recovers after network isolation

    - Enable `raft learner` by default to lower the risk of unavailable data caused by machine failure during scheduling

    - TSO allocation is no longer affected by the system clock going backwards

    - Support the `Region merge` feature to reduce the overhead brought by metadata

+ Optimize the scheduler

    - Optimize the processing of Down Store to speed up making up replicas

    - Optimize the hotspot scheduler to improve its adaptability when traffic statistics information jitters

    - Optimize the start of Coordinator to reduce the unnecessary scheduling caused by restarting PD

    - Optimize the issue that Balance Scheduler schedules small Regions frequently

    - Optimize Region merge to consider the number of rows within the Region

    - [Add more commands to control the scheduling policy](https://docs.pingcap.com/tidb/stable/pd-control#config-show--set-option-value--placement-rules)

    - Improve [PD simulator](https://github.com/pingcap/pd/tree/release-2.1/tools/pd-simulator) to simulate the scheduling scenarios

+ API and operation tools

    - Add the [`GetPrevRegion` interface](https://github.com/pingcap/kvproto/blob/8e3f33ac49297d7c93b61a955531191084a2f685/proto/pdpb.proto#L40) to support the `TiDB reverse scan` feature

    - Add the [`BatchSplitRegion` interface](https://github.com/pingcap/kvproto/blob/8e3f33ac49297d7c93b61a955531191084a2f685/proto/pdpb.proto#L54) to speed up TiKV Region splitting

    - Add the [`GCSafePoint` interface](https://github.com/pingcap/kvproto/blob/8e3f33ac49297d7c93b61a955531191084a2f685/proto/pdpb.proto#L64-L66) to support distributed GC in TiDB

    - Add the [`GetAllStores` interface](https://github.com/pingcap/kvproto/blob/8e3f33ac49297d7c93b61a955531191084a2f685/proto/pdpb.proto#L32), to support distributed GC in TiDB

    + pd-ctl supports:
        - [using statistics for Region split](https://docs.pingcap.com/tidb/stable/pd-control#operator-check--show--add--remove)

        - [calling `jq` to format the JSON output](https://docs.pingcap.com/tidb/stable/pd-control#jq-formatted-json-output-usage)

        - [checking the Region information of the specified store](https://docs.pingcap.com/tidb/stable/pd-control#region-store-store_id)

        - [checking topN Region list sorted by versions](https://docs.pingcap.com/tidb/stable/pd-control#region-topconfver-limit)

        - [checking topN Region list sorted by size](https://docs.pingcap.com/tidb/stable/pd-control#region-topsize-limit)

        - [more precise TSO encoding](https://docs.pingcap.com/tidb/stable/pd-control#tso)

    - [pd-recover](https://docs.pingcap.com/tidb/stable/pd-recover) doesn't need to provide the `max-replica` parameter

+ Metrics

    - Add related metrics for `Filter`

    - Add metrics about etcd Raft state machine

+ Performance

    - Optimize the performance of Region heartbeat to reduce the memory overhead brought by heartbeats

    - Optimize the Region tree performance

    - Optimize the performance of computing hotspot statistics
