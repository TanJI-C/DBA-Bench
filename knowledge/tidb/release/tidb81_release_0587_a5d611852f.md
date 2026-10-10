# Bug fixes for TiDB and TiKV in 8.0.0

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-8.0.0.md`
- Source Title: `TiDB 8.0.0 Release Notes`
- Source Heading Path: `TiDB 8.0.0 Release Notes > Bug fixes`
- Source Line Ranges: `488-525`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `tiflash`, `pd`
- Topic Tags: `bug-fixes`, `sql`, `partitioning`, `ttl`, `memory-usage`, `observability`, `tiflash`, `tls`, `auto-increment`, `configuration`, `region-availability`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0587_a5d611852f`
- Source ID: `tidb-docs-8.1:releases/release-8.0.0.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `728f895260c86b70f7b35403e895e1206daae651516ce9171d2cc27eafca3bdd`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-8.0.0#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-8.0.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking up TiDB 8.0.0 bug fixes for specific errors, SQL correctness issues, TTL behavior, partitioning problems, configuration handling, TiFlash behavior, TLS reload errors, AUTO_INCREMENT conflicts, observability fixes, or TiKV Region and metric issues.
- Retrieval Keywords: TiDB 8.0.0 bug fixes, tidb_gogc_tuner_threshold, tidb_server_memory_limit, index out of range JOIN, default value is dropped, TiFlash late materialization, LIKE() binary collation, JSON_LENGTH() second parameter NULL, CAST(AS DATETIME) lose time precision, parallel Apply clustered index, ALTER TABLE ... COMPACT TIFLASH REPLICA, EXCHANGE PARTITION DEFAULT NULL, INFORMATION_SCHEMA.VARIABLES_INFO, SPLIT TABLE ... INDEX panic, KeyPartition query error, Hash partitioned table incorrect results, opentracing does not work correctly, ALTER INSTANCE RELOAD TLS, AUTO_INCREMENT non-consecutive IDs, LIMIT clause too large excessive memory usage, TTL data hotspots, daylight saving time expiration times, SURVIVAL_PREFERENCES, SHOW CREATE PLACEMENT POLICY, invalid configuration item, tidb_enable_row_level_checksum, hibernated Regions, Region becomes unavailable when one replica is offline, tikv_unified_read_pool_thread_count
- Follow-up Guidance: 
- Classification Note: This is a release-notes bug-fix chunk summarizing resolved issues in TiDB and TiKV for 8.0.0 across SQL execution, partitioning, TTL, observability, configuration, TiFlash, TLS, AUTO_INCREMENT, and Region availability.

## Official Source Content

- Fix the issue that the `tidb_gogc_tuner_threshold` system variable is not adjusted accordingly after the `tidb_server_memory_limit` variable is modified [#48180](https://github.com/pingcap/tidb/issues/48180) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that the `index out of range` error might occur when a query involves JOIN operations [#42588](https://github.com/pingcap/tidb/issues/42588) @[AilinKid](https://github.com/AilinKid)
    - Fix the issue that getting the default value of a column returns an error if the column default value is dropped [#50043](https://github.com/pingcap/tidb/issues/50043) [#51324](https://github.com/pingcap/tidb/issues/51324) @[crazycs520](https://github.com/crazycs520)
    - Fix the issue that wrong results might be returned when TiFlash late materialization processes associated columns [#49241](https://github.com/pingcap/tidb/issues/49241) [#51204](https://github.com/pingcap/tidb/issues/51204) @[Lloyd-Pottiger](https://github.com/Lloyd-Pottiger)
    - Fix the issue that the `LIKE()` function might return wrong results when processing binary collation inputs [#50393](https://github.com/pingcap/tidb/issues/50393) @[yibin87](https://github.com/yibin87)
    - Fix the issue that the `JSON_LENGTH()` function returns wrong results when the second parameter is `NULL` [#50931](https://github.com/pingcap/tidb/issues/50931) @[SeaRise](https://github.com/SeaRise)
    - Fix the issue that `CAST(AS DATETIME)` might lose time precision under certain circumstances [#49555](https://github.com/pingcap/tidb/issues/49555) @[SeaRise](https://github.com/SeaRise)
    - Fix the issue that parallel `Apply` might generate incorrect results when the table has a clustered index [#51372](https://github.com/pingcap/tidb/issues/51372) @[guo-shaoge](https://github.com/guo-shaoge)
    - Fix the issue that `ALTER TABLE ... COMPACT TIFLASH REPLICA` might incorrectly end when the primary key type is `VARCHAR` [#51810](https://github.com/pingcap/tidb/issues/51810) @[breezewish](https://github.com/breezewish)
    - Fix the issue that the check on the `NULL` value of the `DEFAULT NULL` attribute is incorrect when exchanging partitioned tables using the `EXCHANGE PARTITION` statement [#47167](https://github.com/pingcap/tidb/issues/47167) @[jiyfhust](https://github.com/jiyfhust)
    - Fix the issue that the partition table definition might cause wrong behavior when using a non-UTF8 character set [#49251](https://github.com/pingcap/tidb/issues/49251) @[YangKeao](https://github.com/YangKeao)
    - Fix the issue that incorrect default values are displayed in the `INFORMATION_SCHEMA.VARIABLES_INFO` table for some system variables [#49461](https://github.com/pingcap/tidb/issues/49461) @[jiyfhust](https://github.com/jiyfhust)
    - Fix the issue that no error is reported when empty strings are used as database names in some cases [#45873](https://github.com/pingcap/tidb/issues/45873) @[yoshikipom](https://github.com/yoshikipom)
    - Fix the issue that the `SPLIT TABLE ... INDEX` statement might cause TiDB to panic [#50177](https://github.com/pingcap/tidb/issues/50177) @[Defined2014](https://github.com/Defined2014)
    - Fix the issue that querying a partitioned table of `KeyPartition` type might cause an error [#50206](https://github.com/pingcap/tidb/issues/50206) [#51313](https://github.com/pingcap/tidb/issues/51313) [#51196](https://github.com/pingcap/tidb/issues/51196) @[time-and-fate](https://github.com/time-and-fate) @[jiyfhust](https://github.com/jiyfhust) @[mjonss](https://github.com/mjonss)
    - Fix the issue that querying a Hash partitioned table might produce incorrect results [#50427](https://github.com/pingcap/tidb/issues/50427) @[Defined2014](https://github.com/Defined2014)
    - Fix the issue that opentracing does not work correctly [#50508](https://github.com/pingcap/tidb/issues/50508) @[Defined2014](https://github.com/Defined2014)
    - Fix the issue that the error message is not complete when `ALTER INSTANCE RELOAD TLS` reports an error [#50699](https://github.com/pingcap/tidb/issues/50699) @[dveeden](https://github.com/dveeden)
    - Fix the issue that the `AUTO_INCREMENT` attribute causes non-consecutive IDs due to unnecessary transaction conflicts when assigning auto-increment IDs [#50819](https://github.com/pingcap/tidb/issues/50819) @[tiancaiamao](https://github.com/tiancaiamao)
    - Fix the issue of incomplete stack information in TiDB logs for some errors [#50849](https://github.com/pingcap/tidb/issues/50849) @[tiancaiamao](https://github.com/tiancaiamao)
    - Fix the issue of excessive memory usage in some queries when the number in the `LIMIT` clause is too large [#51188](https://github.com/pingcap/tidb/issues/51188) @[Defined2014](https://github.com/Defined2014)
    - Fix the issue that the TTL feature causes data hotspots due to incorrect data range splitting in some cases [#51527](https://github.com/pingcap/tidb/issues/51527) @[lcwangchao](https://github.com/lcwangchao)
    - Fix the issue that the `SET` statement does not take effect when it appears on the first line of an explicit transaction [#51387](https://github.com/pingcap/tidb/issues/51387) @[YangKeao](https://github.com/YangKeao)
    - Fix the issue that querying JSON of `BINARY` type might cause an error in some cases [#51547](https://github.com/pingcap/tidb/issues/51547) @[YangKeao](https://github.com/YangKeao)
    - Fix the issue that TTL does not handle the transition for daylight saving time adjustments correctly when calculating expiration times [#51675](https://github.com/pingcap/tidb/issues/51675) @[lcwangchao](https://github.com/lcwangchao)
    - Fix the issue that the `SURVIVAL_PREFERENCES` attribute might not appear in the output of the `SHOW CREATE PLACEMENT POLICY` statement under certain conditions [#51699](https://github.com/pingcap/tidb/issues/51699) @[lcwangchao](https://github.com/lcwangchao)
    - Fix the issue that the configuration file does not take effect when it contains an invalid configuration item [#51399](https://github.com/pingcap/tidb/issues/51399) @[Defined2014](https://github.com/Defined2014)

+ TiKV

    - Fix the issue that enabling `tidb_enable_row_level_checksum` might cause TiKV to panic [#16371](https://github.com/tikv/tikv/issues/16371) @[cfzjywxk](https://github.com/cfzjywxk)
    - Fix the issue that hibernated Regions are not promptly awakened in exceptional circumstances [#16368](https://github.com/tikv/tikv/issues/16368) @[LykxSassinator](https://github.com/LykxSassinator)
    - Fix the issue that the entire Region becomes unavailable when one replica is offline, by checking the last heartbeat time of all replicas of the Region before taking a node offline [#16465](https://github.com/tikv/tikv/issues/16465) @[tonyxuqqi](https://github.com/tonyxuqqi)
    - Fix the issue that JSON integers greater than the maximum `INT64` value but less than the maximum `UINT64` value are parsed as `FLOAT64` by TiKV, resulting in inconsistency with TiDB [#16512](https://github.com/tikv/tikv/issues/16512) @[YangKeao](https://github.com/YangKeao)
    - Fix the issue that the monitoring metric `tikv_unified_read_pool_thread_count` has no data in some cases [#16629](https://github.com/tikv/tikv/issues/16629) @[YuJuncen](https://github.com/YuJuncen)

+ PD
