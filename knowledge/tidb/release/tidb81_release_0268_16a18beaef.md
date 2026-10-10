# TiDB 5.3.4 release notes: improvements and bug fixes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.3.4.md`
- Source Title: `TiDB 5.3.4 Release Notes`
- Source Heading Path: `TiDB 5.3.4 Release Notes | TiDB 5.3.4 Release Notes > Improvements | TiDB 5.3.4 Release Notes > Bug fixes`
- Source Line Ranges: `5-60`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `tiflash`, `dumpling`, `ticdc`, `dashboard`
- Topic Tags: `release-notes`, `improvements`, `bug-fixes`, `tls`, `region-cache`, `data-correctness`, `privileges`, `authentication`, `sql-functions`, `mpp`, `dashboard-proxy`, `leader-switchover`, `bootstrap`, `s3`, `changefeed`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0268_16a18beaef`
- Source ID: `tidb-docs-8.1:releases/release-5.3.4.md#tidb-5-3-4-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ea8e392f51d24ffca7f77ccfb7b98cf3df83184368db02a18cd5e37ae77879c3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.3.4#tidb-5-3-4-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.3.4.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the official TiDB 5.3.4 release notes that list improvements and bug fixes across TiKV, TiDB, PD, TiFlash, Dumpling, and TiCDC.
- Retrieval Keywords: TiDB 5.3.4 Release Notes, release date November 24, 2022, Reload TLS certificate automatically, Region cache is not cleaned up in time when the Region is merged, wrong encoding of the ENUM or SET column, database-level privileges are incorrectly cleaned up, grantor field is missing in the mysql.tables_priv table, KILL TIDB cannot take effect immediately on idle connections, date_add and date_sub return type, GREATEST and LEAST unsigned BIGINT, avg() ERROR 1105 (HY000): other error for mpp stream, ERROR 1105 (HY000): close of nil channel, EXPLAIN ANALYZE statement with DML executors, dashboard proxy requests, TiFlash learner replica might not be created, accelerate leader switchover, logical operators return wrong results when the argument type is UInt8, TiFlash bootstrap fails when 0.0 is used as the default value for integers, Dumpling --compress option and the S3 output directory, changefeed state is incorrect
- Follow-up Guidance: The source also points to the corresponding GitHub issue numbers for each listed improvement and bug fix.
- Classification Note: This chunk is classified as a self-managed release note because it summarizes official improvements and bug fixes in TiDB 5.3.4 across multiple components.

## Official Source Content

# TiDB 5.3.4 Release Notes

Release date: November 24, 2022

TiDB version: 5.3.4
## Improvements

+ TiKV

    - Reload TLS certificate automatically for each update to improve availability [#12546](https://github.com/tikv/tikv/issues/12546)
## Bug fixes

+ TiDB

    - Fix the issue that the Region cache is not cleaned up in time when the Region is merged [#37141](https://github.com/pingcap/tidb/issues/37141)
    - Fix the issue that TiDB writes wrong data due to the wrong encoding of the `ENUM` or `SET` column [#32302](https://github.com/pingcap/tidb/issues/32302)
    - Fix the issue that database-level privileges are incorrectly cleaned up [#38363](https://github.com/pingcap/tidb/issues/38363)
    - Fix the issue that the `grantor` field is missing in the `mysql.tables_priv` table [#38293](https://github.com/pingcap/tidb/issues/38293)
    - Fix the issue that `KILL TIDB` cannot take effect immediately on idle connections [#24031](https://github.com/pingcap/tidb/issues/24031)
    - Fix the issue that the return type of `date_add` and `date_sub` is different between TiDB and MySQL [#36394](https://github.com/pingcap/tidb/issues/36394), [#27573](https://github.com/pingcap/tidb/issues/27573)
    - Fix the incorrect `INSERT_METHOD` value when Parser restores table options [#38368](https://github.com/pingcap/tidb/issues/38368)
    - Fix the issue that authentication fails when a MySQL client of v5.1 or earlier connects to the TiDB server [#29725](https://github.com/pingcap/tidb/issues/29725)
    - Fix wrong results of `GREATEST` and `LEAST` when passing in unsigned `BIGINT` arguments [#30101](https://github.com/pingcap/tidb/issues/30101)
    - Fix the issue that the result of `concat(ifnull(time(3))` in TiDB is different from that in MySQL [#29498](https://github.com/pingcap/tidb/issues/29498)
    - Fix the issue that the `avg()` function returns `ERROR 1105 (HY000): other error for mpp stream: Could not convert to the target type - -value is out of range.` when queried from TiFlash [#29952](https://github.com/pingcap/tidb/issues/29952)
    - Fix the issue that `ERROR 1105 (HY000): close of nil channel` is returned when using `HashJoinExec` [#30289](https://github.com/pingcap/tidb/issues/30289)
    - Fix the issue that TiKV and TiFlash return different results when querying logical operations [#37258](https://github.com/pingcap/tidb/issues/37258)
    - Fix the issue that the `EXPLAIN ANALYZE` statement with DML executors might return result before the transaction commit finishes [#37373](https://github.com/pingcap/tidb/issues/37373)
    - Fix the issue that Region cache is not cleared properly after merging many Regions [#37174](https://github.com/pingcap/tidb/issues/37174)
    - Fix the issue that the `EXECUTE` statement might throw an unexpected error in specific scenarios [#37187](https://github.com/pingcap/tidb/issues/37187)
    - Fix the issue that `GROUP CONCAT` with `ORDER BY` might fail when the `ORDER BY` clause contains a correlated subquery [#18216](https://github.com/pingcap/tidb/issues/18216)
    - Fix wrong results returned when length and width are incorrectly set for Decimal and Real when using plan cache [#29565](https://github.com/pingcap/tidb/issues/29565)

+ PD

    - Fix the issue that PD cannot correctly handle dashboard proxy requests [#5321](https://github.com/tikv/pd/issues/5321)
    - Fix the issue that the TiFlash learner replica might not be created in specific scenarios [#5401](https://github.com/tikv/pd/issues/5401)
    - Fix inaccurate Stream timeout and accelerate leader switchover [#5207](https://github.com/tikv/pd/issues/5207)

+ TiFlash

    - Fix the issue that logical operators return wrong results when the argument type is UInt8 [#6127](https://github.com/pingcap/tiflash/issues/6127)
    - Fix the issue that TiFlash bootstrap fails when `0.0` is used as the default value for integers, for example, `` `i` int(11) NOT NULL DEFAULT '0.0'`` [#3157](https://github.com/pingcap/tiflash/issues/3157)

+ Tools

    + Dumpling

        - Fix the issue that Dumpling cannot dump data when the `--compress` option and the S3 output directory are set simultaneously [#30534](https://github.com/pingcap/tidb/issues/30534)

    + TiCDC

        - Fix the issue that changefeed state is incorrect because a MySQL-related error is not reported to the owner in time [#6698](https://github.com/pingcap/tiflow/issues/6698)
