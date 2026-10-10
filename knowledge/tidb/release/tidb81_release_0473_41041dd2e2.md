# Bug fixes for TiDB and TiKV

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.1.4.md`
- Source Title: `TiDB 7.1.4 Release Notes`
- Source Heading Path: `TiDB 7.1.4 Release Notes > Bug fixes`
- Source Line Ranges: `99-126`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `ticdc`, `tiflash`, `shared`
- Topic Tags: `bug-fixes`, `ddl`, `indexing`, `memory`, `partition-pruning`, `statistics`, `join`, `query-correctness`, `region`, `replication`, `grpc`, `timezone`, `json`, `decimal`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0473_41041dd2e2`
- Source ID: `tidb-docs-8.1:releases/release-7.1.4.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `752a0fde5bde2eaee4f7c5a089b3e4fa06c2a302fb0762987ddc1776d600ab70`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.1.4#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.1.4.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 7.1.4 bug fixes related to DDL, index creation, memory limits, partition pruning, statistics, JOIN errors, TiFlash query correctness, or TiKV issues involving Regions, gRPC, DECIMAL, time zone, JSON, and tikv-ctl.
- Retrieval Keywords: TiDB 7.1.4 bug fixes, adding an index to an empty table, inconsistent index data unstable network, TiCDC out-of-order DDLs, tidb_gogc_tuner_threshold, tidb_server_memory_limit, wrong partition pruning, CREATE TABLE specific partitions or constraints, tidb_statistics_auto_analyze_total, tidb_merge_partition_stats_concurrency, index out of range JOIN, TiFlash late materialization associated columns, parallel Apply clustered index, hibernated Regions, tikv-ctl compact-cluster, gRPC threads is_shutdown, DECIMAL arithmetic multiplication truncation, cast_duration_as_time, Brazil and Egypt time zone, JSON INT64 UINT64 FLOAT64
- Follow-up Guidance: 
- Classification Note: This is a release-note bug-fix chunk covering TiDB and TiKV fixes in TiDB 7.1.4 for self-managed deployments.

## Official Source Content

- Fix the issue that the expected optimization does not take effect when adding an index to an empty table [#49682](https://github.com/pingcap/tidb/issues/49682) @[zimulala](https://github.com/zimulala)
    - Fix the issue that TiDB might OOM when a large number of tables or partitions are created [#50077](https://github.com/pingcap/tidb/issues/50077) @[zimulala](https://github.com/zimulala)
    - Fix the issue that adding an index might cause inconsistent index data when the network is unstable [#49773](https://github.com/pingcap/tidb/issues/49773) @[tangenta](https://github.com/tangenta)
    - Fix the execution order of DDL jobs to prevent TiCDC from receiving out-of-order DDLs [#49498](https://github.com/pingcap/tidb/issues/49498) @[tangenta](https://github.com/tangenta)
    - Fix the issue that the `tidb_gogc_tuner_threshold` system variable is not adjusted accordingly after the `tidb_server_memory_limit` variable is modified [#48180](https://github.com/pingcap/tidb/issues/48180) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that the query result of a range partitioned table is incorrect in some cases due to wrong partition pruning [#50082](https://github.com/pingcap/tidb/issues/50082) @[Defined2014](https://github.com/Defined2014)
    - Fix the issue that DDL operations such as renaming tables are stuck when the `CREATE TABLE` statement contains specific partitions or constraints [#50972](https://github.com/pingcap/tidb/issues/50972) @[lcwangchao](https://github.com/lcwangchao)
    - Fix the issue that getting the default value of a column returns an error if the column default value is dropped [#50043](https://github.com/pingcap/tidb/issues/50043) [#51324](https://github.com/pingcap/tidb/issues/51324) @[crazycs520](https://github.com/crazycs520)
    - Fix the issue that the monitoring metric `tidb_statistics_auto_analyze_total` on Grafana is not displayed as an integer [#51051](https://github.com/pingcap/tidb/issues/51051) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that the `tidb_merge_partition_stats_concurrency` variable does not take effect when `auto analyze` is processing partitioned tables [#47594](https://github.com/pingcap/tidb/issues/47594) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that the `index out of range` error might occur when a query involves JOIN operations [#42588](https://github.com/pingcap/tidb/issues/42588) @[AilinKid](https://github.com/AilinKid)
    - Fix the issue that wrong results might be returned when TiFlash late materialization processes associated columns [#49241](https://github.com/pingcap/tidb/issues/49241) [#51204](https://github.com/pingcap/tidb/issues/51204) @[Lloyd-Pottiger](https://github.com/Lloyd-Pottiger)
    - Fix the issue that parallel `Apply` might generate incorrect results when the table has a clustered index [#51372](https://github.com/pingcap/tidb/issues/51372) @[guo-shaoge](https://github.com/guo-shaoge)

+ TiKV

    - Fix the issue that hibernated Regions are not promptly awakened in exceptional circumstances [#16368](https://github.com/tikv/tikv/issues/16368) @[LykxSassinator](https://github.com/LykxSassinator)
    - Fix the issue that the entire Region becomes unavailable when one replica is offline, by checking the last heartbeat time of all replicas of the Region before taking a node offline [#16465](https://github.com/tikv/tikv/issues/16465) @[tonyxuqqi](https://github.com/tonyxuqqi)
    - Fix the issue that table properties stored in RocksDB might be inaccurate when Titan is enabled [#16319](https://github.com/tikv/tikv/issues/16319) @[hicqu](https://github.com/hicqu)
    - Fix the issue that executing `tikv-ctl compact-cluster` fails when a cluster has TiFlash nodes [#16189](https://github.com/tikv/tikv/issues/16189) @[frew](https://github.com/frew)
    - Fix the issue that TiKV might panic when gRPC threads are checking `is_shutdown` [#16236](https://github.com/tikv/tikv/issues/16236) @[pingyu](https://github.com/pingyu)
    - Fix the issue that TiDB and TiKV might produce inconsistent results when processing `DECIMAL` arithmetic multiplication truncation [#16268](https://github.com/tikv/tikv/issues/16268) @[solotzg](https://github.com/solotzg)
    - Fix the issue that `cast_duration_as_time` might return incorrect results [#16211](https://github.com/tikv/tikv/issues/16211) @[gengliqi](https://github.com/gengliqi)
    - Fix the issue that TiKV converts the time zone incorrectly for Brazil and Egypt [#16220](https://github.com/tikv/tikv/issues/16220) @[overvenus](https://github.com/overvenus)
    - Fix the issue that JSON integers greater than the maximum `INT64` value but less than the maximum `UINT64` value are parsed as `FLOAT64` by TiKV, resulting in inconsistency with TiDB [#16512](https://github.com/tikv/tikv/issues/16512) @[YangKeao](https://github.com/YangKeao)

+ PD
