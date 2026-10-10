# TiDB 6.1.3 bug fixes across TiDB, PD, TiKV, TiFlash, BR, TiCDC, and DM

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.1.3.md`
- Source Title: `TiDB 6.1.3 Release Notes`
- Source Heading Path: `TiDB 6.1.3 Release Notes > Bug fixes`
- Source Line Ranges: `39-85`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `pd`, `tikv`, `tiflash`, `br`, `ticdc`, `dm`
- Topic Tags: `release-notes`, `bug-fixes`, `security`, `privileges`, `query-results`, `locks`, `auto-increment`, `grpc-logs`, `etcd`, `statistics`, `pessimistic-lock`, `leader-switchover`, `region`, `snapshot`, `delta-layer`, `restore`, `data-loss`, `changefeed`, `network`, `collation`, `placement-policy`, `relay-log`, `worker-scheduling`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0313_848b571ca4`
- Source ID: `tidb-docs-8.1:releases/release-6.1.3.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6f8096ebca1507d665243d0912c4bac6fd14e7894d4f62284b7ad2fe60774a99`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.1.3#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.1.3.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving the TiDB 6.1.3 bug fixes for specific issues across TiDB, PD, TiKV, TiFlash, BR, TiCDC, and DM.
- Retrieval Keywords: TiDB 6.1.3 bug fixes, mysql.tables_priv grantor field missing, wrong query result Join Reorder, get_lock() cannot hold for more than 10 minutes, auto-increment column cannot be used with check constraint, gRPC log output to wrong file, TiFlash sync status not deleted from etcd, CVE-2022-3023, data source name injection, str_to_date NO_ZERO_DATE wrong result, statistics collection tasks panic, pessimistic lock non-unique secondary index, PD Stream timeout leader switchover, TiKV expired lease during snapshot acquisition, TiFlash UInt8 logical operators wrong results, CAST(value AS DATETIME) high TiFlash sys CPU, delta layer column files, BR old framework for collations restore tasks fail, TiCDC data loss pause and resume changefeed after DDL, sink component gets stuck if the downstream network is unavailable, DM collation_compatible strict duplicated collations, Unknown placement policy, relay logs pulled from upstream again, new DM worker scheduled before existing worker exits
- Follow-up Guidance: 
- Classification Note: This is a release bug-fix chunk because it enumerates resolved issues by component in the TiDB 6.1.3 release notes.

## Official Source Content

## Bug fixes

+ TiDB

    - Fix the issue that the `grantor` field is missing in the `mysql.tables_priv` table [#38293](https://github.com/pingcap/tidb/issues/38293) @[CbcWestwolf](https://github.com/CbcWestwolf)
    - Fix the issue of the wrong query result that occurs when the mistakenly pushed-down conditions are discarded by Join Reorder [#38736](https://github.com/pingcap/tidb/issues/38736) @[winoros](https://github.com/winoros)
    - Fix the issue that the lock acquired by `get_lock()` cannot hold for more than 10 minutes [#38706](https://github.com/pingcap/tidb/issues/38706) @[tangenta](https://github.com/tangenta)
    - Fix the issue that the auto-increment column cannot be used with check constraint [#38894](https://github.com/pingcap/tidb/issues/38894) @[YangKeao](https://github.com/YangKeao)
    - Fix the issue that the gPRC log is output to a wrong file [#38941](https://github.com/pingcap/tidb/issues/38941) @[xhebox](https://github.com/xhebox)
    - Fix the issue that the TiFlash sync status of a table is not deleted from etcd when the table is truncated or dropped [#37168](https://github.com/pingcap/tidb/issues/37168) @[CalvinNeo](https://github.com/CalvinNeo)
    - Fix the issue that data files can be accessed unrestrainedly via data source name injection (CVE-2022-3023) [#38541](https://github.com/pingcap/tidb/issues/38541) @[lance6716](https://github.com/lance6716)
    - Fix the issue that the function `str_to_date` returns wrong result in the `NO_ZERO_DATE` SQL mode [#39146](https://github.com/pingcap/tidb/issues/39146) @[mengxin9014](https://github.com/mengxin9014)
    - Fix the issue that statistics collection tasks in the background might panic [#35421](https://github.com/pingcap/tidb/issues/35421) @[lilinghai](https://github.com/lilinghai)
    - Fix the issue that in some scenarios the pessimistic lock is incorrectly added to the non-unique secondary index [#36235](https://github.com/pingcap/tidb/issues/36235) @[ekexium](https://github.com/ekexium)

- PD

    - Fix inaccurate Stream timeout and accelerate leader switchover [#5207](https://github.com/tikv/pd/issues/5207) @[CabinfeverB](https://github.com/CabinfeverB)

+ TiKV

    - Fix abnormal Region competition caused by expired lease during snapshot acquisition [#13553](https://github.com/tikv/tikv/issues/13553) @[SpadeA-Tang](https://github.com/SpadeA-Tang)

+ TiFlash

    - Fix the issue that logical operators return wrong results when the argument type is `UInt8` [#6127](https://github.com/pingcap/tiflash/issues/6127) @[xzhangxian1008](https://github.com/xzhangxian1008)
    - Fix the issue that wrong data input for `CAST(value AS DATETIME)` causing high TiFlash sys CPU [#5097](https://github.com/pingcap/tiflash/issues/5097) @[xzhangxian1008](https://github.com/xzhangxian1008)
    - Fix the issue that heavy write pressure might generate too many column files in the delta layer [#6361](https://github.com/pingcap/tiflash/issues/6361) @[lidezhu](https://github.com/lidezhu)
    - Fix the issue that column files in the delta layer cannot be compacted after restarting TiFlash [#6159](https://github.com/pingcap/tiflash/issues/6159) @[lidezhu](https://github.com/lidezhu)

+ Tools

    + Backup & Restore (BR)

        - Fix the issue that restore tasks fail when using old framework for collations in databases or tables [#39150](https://github.com/pingcap/tidb/issues/39150) @[MoCuishle28](https://github.com/MoCuishle28)

    + TiCDC

        - Fix data loss occurred in the scenario of executing DDL statements first and then pausing and resuming the changefeed [#7682](https://github.com/pingcap/tiflow/issues/7682) @[asddongmen](https://github.com/asddongmen)
        - Fix the issue that the sink component gets stuck if the downstream network is unavailable [#7706](https://github.com/pingcap/tiflow/issues/7706) @[hicqu](https://github.com/hicqu)

    + TiDB Data Migration (DM)

        - Fix the issue that when `collation_compatible` is set to `"strict"`, DM might generate SQL with duplicated collations [#6832](https://github.com/pingcap/tiflow/issues/6832) @[lance6716](https://github.com/lance6716)
        - Fix the issue that DM tasks might stop with an `Unknown placement policy` error [#7493](https://github.com/pingcap/tiflow/issues/7493) @[lance6716](https://github.com/lance6716)
        - Fix the issue that relay logs might be pulled from upstream again in some cases [#7525](https://github.com/pingcap/tiflow/issues/7525) @[liumengya94](https://github.com/liumengya94)
        - Fix the issue that data is replicated for multiple times when a new DM worker is scheduled before the existing worker exits [#7658](https://github.com/pingcap/tiflow/issues/7658) @[GMHDBJD](https://github.com/GMHDBJD)
