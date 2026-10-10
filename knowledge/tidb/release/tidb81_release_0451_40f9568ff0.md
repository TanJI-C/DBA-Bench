# TiDB 7.1.0 bug fixes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.1.0.md`
- Source Title: `TiDB 7.1.0 Release Notes`
- Source Heading Path: `TiDB 7.1.0 Release Notes > Bug fixes`
- Source Line Ranges: `420-457`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `pd`, `tiflash`, `shared`
- Topic Tags: `bug-fixes`, `ddl`, `partitioned-tables`, `global-index`, `information-schema`, `grafana`, `ttl`, `ipv6`, `analyze-table`, `system-variables`, `metadata-locks`, `auto-increment`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0451_40f9568ff0`
- Source ID: `tidb-docs-8.1:releases/release-7.1.0.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1846464709f5b1f45c80ad6211734979593fb8af1640ac077f7349eb08e9e08c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.1.0#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.1.0.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 7.1.0 bug fix coverage for issues involving DDL, partitioned tables, global indexes, INFORMATION_SCHEMA, Grafana panels, TTL monitoring, IPv6, ANALYZE TABLE, metadata locks, AUTO_INCREMENT, or related error messages.
- Retrieval Keywords: TiDB 7.1.0 bug fixes, ANALYZE TABLE after reorganizing partitions, ADMIN SHOW DDL JOBS missing table names DROP TABLE, Ignore Event Per Minute, Stats Cache LRU Cost, Grafana monitoring panel, ORDINAL_POSITION, INFORMATION_SCHEMA.COLUMNS, cache table NULL instead of default value, CTE results incorrect when pushing down predicates, TRUNCATE TABLE partitioned tables many partitions TiFlash replicas, SUBPARTITION warning creating partitioned tables, value overflow generated columns, REORGANIZE PARTITION concurrently executed with other DDL operations, canceling the partition reorganization task in DDL, assertions on delete operations are incorrect, can't read file memory.stat from cgroup v1, Duplicate Key partition key global index, Scan Worker Time By Phase, TTL monitoring panel, partitioned tables with a global index return incorrect results, INFORMATION_SCHEMA.DDL_JOBS QUERY column, INFORMATION_SCHEMA.CLUSTER_HARDWARE, ORDER BY LIMIT partitioned table incorrect result, multiple DDL tasks running simultaneously using the ingest method, displaying the incorrect TiDB address in IPv6 environment, tidb_enable_tiflash_read_for_write_stmt, tidb_enable_exchange_partition, tidb_scatter_region, generated columns unsupported DDL operations, type conversion errors incorrect error message, TiDB node is normally shutdown DDL tasks canceled, PD member address changes AUTO_INCREMENT blocked for a long time, GC lifetime is shorter than transaction duration, metadata locks unexpectedly block the DDL execution, system views in IPv6 environment, dynamic pruning mode inner join not finding the partition, TiDB reports syntax errors when analyzing tables
- Follow-up Guidance: The source lists specific fixed issues such as `Duplicate Key` on partitioned tables with a global index, `GC lifetime is shorter than transaction duration` during DDL execution, and the cgroup startup error `can't read file memory.stat from cgroup v1: open /sys/memory.stat no such file or directory`.
- Classification Note: This chunk is classified as a TiDB release bug-fix summary because the official content is the Bug fixes section of the TiDB 7.1.0 release notes and enumerates resolved TiDB issues across related components and features.

## Official Source Content

## Bug fixes

+ TiDB

    - Fix the issue that there is no prompt about manually executing `ANALYZE TABLE` after reorganizing partitions [#42183](https://github.com/pingcap/tidb/issues/42183) @[CbcWestwolf](https://github.com/CbcWestwolf)
    - Fix the issue of missing table names in the `ADMIN SHOW DDL JOBS` result when a `DROP TABLE` operation is being executed [#42268](https://github.com/pingcap/tidb/issues/42268) @[tiancaiamao](https://github.com/tiancaiamao)
    - Fix the issue that `Ignore Event Per Minute` and `Stats Cache LRU Cost` charts might not be displayed normally in the Grafana monitoring panel [#42562](https://github.com/pingcap/tidb/issues/42562) @[pingandb](https://github.com/pingandb)
    - Fix the issue that the `ORDINAL_POSITION` column returns incorrect results when querying the `INFORMATION_SCHEMA.COLUMNS` table [#43379](https://github.com/pingcap/tidb/issues/43379) @[bb7133](https://github.com/bb7133)
    - Fix the issue that after a new column is added in the cache table, the value is `NULL` instead of the default value of the column [#42928](https://github.com/pingcap/tidb/issues/42928) @[lqs](https://github.com/lqs)
    - Fix the issue that CTE results are incorrect when pushing down predicates [#43645](https://github.com/pingcap/tidb/issues/43645) @[winoros](https://github.com/winoros)
    - Fix the issue of DDL retry caused by write conflict when executing `TRUNCATE TABLE` for partitioned tables with many partitions and TiFlash replicas [#42940](https://github.com/pingcap/tidb/issues/42940) @[mjonss](https://github.com/mjonss)
    - Fix the issue that there is no warning when using `SUBPARTITION` in creating partitioned tables [#41198](https://github.com/pingcap/tidb/issues/41198) [#41200](https://github.com/pingcap/tidb/issues/41200) @[mjonss](https://github.com/mjonss)
    - Fix the incompatibility issue with MySQL when dealing with value overflow issues in generated columns [#40066](https://github.com/pingcap/tidb/issues/40066) @[jiyfhust](https://github.com/jiyfhust)
    - Fix the issue that `REORGANIZE PARTITION` cannot be concurrently executed with other DDL operations [#42442](https://github.com/pingcap/tidb/issues/42442) @[bb7133](https://github.com/bb7133)
    - Fix the issue that canceling the partition reorganization task in DDL might cause subsequent DDL operations to fail [#42448](https://github.com/pingcap/tidb/issues/42448) @[lcwangchao](https://github.com/lcwangchao)
    - Fix the issue that assertions on delete operations are incorrect under certain conditions [#42426](https://github.com/pingcap/tidb/issues/42426) @[tiancaiamao](https://github.com/tiancaiamao)
    - Fix the issue that TiDB server cannot start due to an error in reading the cgroup information with the error message "can't read file memory.stat from cgroup v1: open /sys/memory.stat no such file or directory" [#42659](https://github.com/pingcap/tidb/issues/42659) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the `Duplicate Key` issue that occurs when updating the partition key of a row on a partitioned table with a global index [#42312](https://github.com/pingcap/tidb/issues/42312) @[L-maple](https://github.com/L-maple)
    - Fix the issue that the `Scan Worker Time By Phase` chart in the TTL monitoring panel does not display data [#42515](https://github.com/pingcap/tidb/issues/42515) @[lcwangchao](https://github.com/lcwangchao)
    - Fix the issue that some queries on partitioned tables with a global index return incorrect results [#41991](https://github.com/pingcap/tidb/issues/41991) [#42065](https://github.com/pingcap/tidb/issues/42065) @[L-maple](https://github.com/L-maple)
    - Fix the issue of displaying some error logs during the process of reorganizing a partitioned table [#42180](https://github.com/pingcap/tidb/issues/42180) @[mjonss](https://github.com/mjonss)
    - Fix the issue that the data length in the `QUERY` column of the `INFORMATION_SCHEMA.DDL_JOBS` table might exceed the column definition [#42440](https://github.com/pingcap/tidb/issues/42440) @[tiancaiamao](https://github.com/tiancaiamao)
    - Fix the issue that the `INFORMATION_SCHEMA.CLUSTER_HARDWARE` table might display incorrect values in containers [#42851](https://github.com/pingcap/tidb/issues/42851) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that an incorrect result is returned when you query a partitioned table using `ORDER BY` + `LIMIT` [#43158](https://github.com/pingcap/tidb/issues/43158) @[Defined2014](https://github.com/Defined2014)
    - Fix the issue of multiple DDL tasks running simultaneously using the ingest method [#42903](https://github.com/pingcap/tidb/issues/42903) @[tangenta](https://github.com/tangenta)
    - Fix the wrong value returned when querying a partitioned table using `Limit` [#24636](https://github.com/pingcap/tidb/issues/24636)
    - Fix the issue of displaying the incorrect TiDB address in IPv6 environment [#43260](https://github.com/pingcap/tidb/issues/43260) @[nexustar](https://github.com/nexustar)
    - Fix the issue of displaying incorrect values for system variables `tidb_enable_tiflash_read_for_write_stmt` and `tidb_enable_exchange_partition` [#43281](https://github.com/pingcap/tidb/issues/43281) @[gengliqi](https://github.com/gengliqi)
    - Fix the issue that when `tidb_scatter_region` is enabled, Region does not automatically split after a partition is truncated [#43174](https://github.com/pingcap/tidb/issues/43174) [#43028](https://github.com/pingcap/tidb/issues/43028) @[jiyfhust](https://github.com/jiyfhust)
    - Add checks on the tables with generated columns and report errors for unsupported DDL operations on these columns [#38988](https://github.com/pingcap/tidb/issues/38988) [#24321](https://github.com/pingcap/tidb/issues/24321) @[tiancaiamao](https://github.com/tiancaiamao)
    - Fix the issue that the error message is incorrect in certain type conversion errors [#41730](https://github.com/pingcap/tidb/issues/41730) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that after a TiDB node is normally shutdown, DDL tasks triggered on this node will be canceled [#43854](https://github.com/pingcap/tidb/issues/43854) @[zimulala](https://github.com/zimulala)
    - Fix the issue that when the PD member address changes, allocating ID for the `AUTO_INCREMENT` column will be blocked for a long time [#42643](https://github.com/pingcap/tidb/issues/42643) @[tiancaiamao](https://github.com/tiancaiamao)
    - Fix the issue of reporting the `GC lifetime is shorter than transaction duration` error during DDL execution [#40074](https://github.com/pingcap/tidb/issues/40074) @[tangenta](https://github.com/tangenta)
    - Fix the issue that metadata locks unexpectedly block the DDL execution [#43755](https://github.com/pingcap/tidb/issues/43755) @[wjhuang2016](https://github.com/wjhuang2016)
    - Fix the issue that the cluster cannot query some system views in IPv6 environment [#43286](https://github.com/pingcap/tidb/issues/43286) @[Defined2014](https://github.com/Defined2014)
    - Fix the issue of not finding the partition during inner join in dynamic pruning mode [#43686](https://github.com/pingcap/tidb/issues/43686) @[mjonss](https://github.com/mjonss)
    - Fix the issue that TiDB reports syntax errors when analyzing tables [#43392](https://github.com/pingcap/tidb/issues/43392) @[guo-shaoge](https://github.com/guo-shaoge)
