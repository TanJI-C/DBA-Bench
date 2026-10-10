# TiDB 4.0.6 release notes: new features and improvements

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-4.0.6.md`
- Source Title: `TiDB 4.0.6 Release Notes`
- Source Heading Path: `TiDB 4.0.6 Release Notes | TiDB 4.0.6 Release Notes > New Features | TiDB 4.0.6 Release Notes > Improvements`
- Source Line Ranges: `5-96`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `tiflash`, `dashboard`, `ticdc`, `br`, `dumpling`, `lightning`
- Topic Tags: `release-notes`, `new-features`, `improvements`, `dashboard`, `outer-join`, `performance`, `observability`, `tooling`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0186_b051c4a92c`
- Source ID: `tidb-docs-8.1:releases/release-4.0.6.md#tidb-4-0-6-release-notes`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `dc1282e6330400e44cc7df808b3a8d300cd0f856bda043baaeb68bfccfa540c4`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-4.0.6#tidb-4-0-6-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-4.0.6.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the official TiDB 4.0.6 release notes that summarize new features and improvements across TiDB, TiKV, PD, TiFlash, TiDB Dashboard, and related tools.
- Retrieval Keywords: TiDB 4.0.6 Release Notes, September 15, 2020, TiCDC GA since v4.0.6, TiFlash support outer join in broadcast join, TiDB Dashboard Query Editor and execution UI, store location topology visualization, cluster configuration UI, sharing the current session, number of execution plans in SQL Statement list, standard errors, partitioned table write performance, Cop Runtime statistics, metrics_schema, performance_schema, union executor concurrency, SQL digest for the process list, Str_to_date() %r %T, SELECT INTO OUTFILE file privilege, stddev_pop, TiDB-Runtime dashboard, ALTER TABLE algorithms, slow log plan field, rocksdb perf context panel, Region and store heartbeat metrics, apply Region snapshots, ingest SST files, write stall, dt_segment_force_merge_delta_rows, dt_segment_force_merge_delta_deletes, raftstore.snap-handle-pool-size, https_port, metrics_port, Skip resolved lock during puller initialization, Reduce PD write frequency, BR real time cost in summary log, Dumpling INSERT with column names, --filesize, --statement-size, TiDB Lightning precise Region split and ingest, TiDB Binlog GC time go time package format
- Follow-up Guidance: 
- Classification Note: The official content is a self-managed release-notes summary for TiDB 4.0.6 covering new features and improvements in shared and component-specific areas.

## Official Source Content

# TiDB 4.0.6 Release Notes

Release date: September 15, 2020

TiDB version: 4.0.6
## New Features

+ TiFlash

    - Support outer join in TiFlash broadcast join

+ TiDB Dashboard

    - Add Query Editor and execution UI (experimental) [#713](https://github.com/pingcap-incubator/tidb-dashboard/pull/713)
    - Support store location topology visualization [#719](https://github.com/pingcap-incubator/tidb-dashboard/pull/719)
    - Add cluster configuration UI (experimental) [#733](https://github.com/pingcap-incubator/tidb-dashboard/pull/733)
    - Support sharing the current session [#741](https://github.com/pingcap-incubator/tidb-dashboard/pull/741)
    - Support displaying the number of execution plans in SQL Statement list [#746](https://github.com/pingcap-incubator/tidb-dashboard/pull/746)

+ Tools

    + TiCDC (GA since v4.0.6)
## Improvements

+ TiDB

    - Replace error codes and messages with standard errors [#19888](https://github.com/pingcap/tidb/pull/19888)
    - Improve the write performance of partitioned table [#19649](https://github.com/pingcap/tidb/pull/19649)
    - Record more RPC runtime information in `Cop Runtime` statistics [#19264](https://github.com/pingcap/tidb/pull/19264)
    - Forbid creating tables in `metrics_schema` and `performance_schema` [#19792](https://github.com/pingcap/tidb/pull/19792)
    - Support adjusting the concurrency of the union executor [#19886](https://github.com/pingcap/tidb/pull/19886)
    - Support out join in broadcast join [#19664](https://github.com/pingcap/tidb/pull/19664)
    - Add SQL digest for the process list [#19829](https://github.com/pingcap/tidb/pull/19829)
    - Switch to the pessimistic transaction mode for autocommit statement retry [#19796](https://github.com/pingcap/tidb/pull/19796)
    - Support the `%r` and `%T` data format in `Str_to_date()` [#19693](https://github.com/pingcap/tidb/pull/19693)
    - Enable `SELECT INTO OUTFILE` to require the file privilege [#19577](https://github.com/pingcap/tidb/pull/19577)
    - Support the `stddev_pop` function [#19541](https://github.com/pingcap/tidb/pull/19541)
    - Add the `TiDB-Runtime` dashboard [#19396](https://github.com/pingcap/tidb/pull/19396)
    - Improve compatibility for the `ALTER TABLE` algorithms [#19364](https://github.com/pingcap/tidb/pull/19364)
    - Encode `insert`/`delete`/`update` plans in the slow log `plan` field [#19269](https://github.com/pingcap/tidb/pull/19269)

+ TiKV

    - Reduce QPS drop when `DropTable` or `TruncateTable` is being executed [#8627](https://github.com/tikv/tikv/pull/8627)
    - Support generating metafile of error codes [#8619](https://github.com/tikv/tikv/pull/8619)
    - Add performance statistics for cf scan details [#8618](https://github.com/tikv/tikv/pull/8618)
    - Add the `rocksdb perf context` panel in the Grafana default template [#8467](https://github.com/tikv/tikv/pull/8467)

+ PD

    - Update TiDB Dashboard to v2020.09.08.1 [#2928](https://github.com/pingcap/pd/pull/2928)
    - Add more metrics for Region and store heartbeat [#2891](https://github.com/tikv/pd/pull/2891)
    - Change back to the original way to control the low space threshold [#2875](https://github.com/pingcap/pd/pull/2875)
    - Support standard error codes
        - [#2918](https://github.com/tikv/pd/pull/2918) [#2911](https://github.com/tikv/pd/pull/2911) [#2913](https://github.com/tikv/pd/pull/2913) [#2915](https://github.com/tikv/pd/pull/2915) [#2912](https://github.com/tikv/pd/pull/2912)
        - [#2907](https://github.com/tikv/pd/pull/2907) [#2906](https://github.com/tikv/pd/pull/2906) [#2903](https://github.com/tikv/pd/pull/2903) [#2806](https://github.com/tikv/pd/pull/2806) [#2900](https://github.com/tikv/pd/pull/2900) [#2902](https://github.com/tikv/pd/pull/2902)

+ TiFlash

    - Add Grafana panels for data replication (`apply Region snapshots` and `ingest SST files`)
    - Add Grafana panels for `write stall`
    - Add `dt_segment_force_merge_delta_rows` and `dt_segment_force_merge_delta_deletes` to adjust the threshold of `write stall`
    - Support setting `raftstore.snap-handle-pool-size` to `0` in TiFlash-Proxy to disable applying Region snapshot by multi-thread to reduce memory consumption during data replication
    - Support CN check on `https_port` and `metrics_port`

+ Tools

    + TiCDC

        - Skip resolved lock during puller initialization [#910](https://github.com/pingcap/tiflow/pull/910)
        - Reduce PD write frequency [#937](https://github.com/pingcap/tiflow/pull/937)

    + Backup & Restore (BR)

        - Add real time cost in summary log [#486](https://github.com/pingcap/br/issues/486)

    + Dumpling

        - Support outputting `INSERT` with column names [#135](https://github.com/pingcap/dumpling/pull/135)
        - Unify the `--filesize` and `--statement-size` definitions with those of mydumper [#142](https://github.com/pingcap/dumpling/pull/142)

    + TiDB Lightning

        - Split and ingest Regions in more precise sizes [#369](https://github.com/pingcap/tidb-lightning/pull/369)

    + TiDB Binlog

        - Support setting GC time in `go time` package format [#996](https://github.com/pingcap/tidb-binlog/pull/996)
