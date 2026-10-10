# TiDB 5.0.3 release overview, compatibility changes, enhancements, and improvements

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.0.3.md`
- Source Title: `TiDB 5.0.3 Release Notes`
- Source Heading Path: `TiDB 5.0.3 Release Notes | TiDB 5.0.3 Release Notes > Compatibility Changes | TiDB 5.0.3 Release Notes > Feature Enhancements | TiDB 5.0.3 Release Notes > Improvements`
- Source Line Ranges: `5-74`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `dashboard`, `tiflash`, `ticdc`
- Topic Tags: `release-notes`, `compatibility`, `feature-enhancements`, `improvements`, `mysql-compatibility`, `pushdown`, `mpp`, `memory-consumption`, `http-api`, `kafka`, `sasl`, `scram`, `dashboard`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0210_ebb7a5f009`
- Source ID: `tidb-docs-8.1:releases/release-5.0.3.md#tidb-5-0-3-release-notes`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6b6726c450de94ca1c5c6b2a7111e73f460244821376bd85d17ef0cb45f27281`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.0.3#tidb-5-0-3-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.0.3.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 5.0.3 release-note coverage of compatibility changes, new TiCDC capabilities, and performance or pushdown improvements across TiDB, TiKV, PD, and TiFlash.
- Retrieval Keywords: TiDB 5.0.3 Release Notes, Compatibility Changes, tidb_multi_statement_mode, WARN to OFF, innodb_default_row_format, TiCDC HTTP API changefeed information health information, SASL/SCRAM kafka sink, --data-dir server level, TopN pushdown to TiFlash, Limit pushdown to TiFlash, json_unquote() pushdown to TiKV, replace() pushdown to TiFlash, unix_timestamp() concat() year() day() datediff() datesub() concat_ws() pushdown to TiFlash, str_to_date pushdown to TiFlash, MPP outer join build table based on table row count, Broadcast Cartesian join to TiFlash, Union All pushdown to TiFlash, balance MPP query workload among TiFlash nodes based on Regions, invalidate stale Regions in cache after MPP query, TiCDC sink memory consumption, TiCDC old value cache memory-bounded upper limit, TiDB Dashboard v2021.06.15.1
- Follow-up Guidance: The same release notes also include a separate Bug Fixes section for TiDB, TiKV, PD, TiFlash, TiCDC, BR, and TiDB Lightning.
- Classification Note: This is a release-notes summary chunk covering TiDB 5.0.3 compatibility changes, feature enhancements, and improvements for multiple components.

## Official Source Content

# TiDB 5.0.3 Release Notes

Release date: July 2, 2021

TiDB version: 5.0.3
## Compatibility Changes

+ TiDB

    - After a v4.0 cluster is upgraded to v5.0 or a later version (dev or v5.1), the default value of the `tidb_multi_statement_mode` variable changes from `WARN` to `OFF`
    - TiDB is now compatible with MySQL 5.7's noop variable `innodb_default_row_format`. Setting this variable will have no effect. [#23541](https://github.com/pingcap/tidb/issues/23541)
## Feature Enhancements

+ Tools

    + TiCDC

        - Add an HTTP API to get the changefeed information and the health information of the node [#1955](https://github.com/pingcap/tiflow/pull/1955)
        - Add the SASL/SCRAM support for the kafka sink [#1942](https://github.com/pingcap/tiflow/pull/1942)
        - Make TiCDC support `--data-dir` at the server level [#2070](https://github.com/pingcap/tiflow/pull/2070)
## Improvements

+ TiDB

    - Support pushing down the `TopN` operator to TiFlash [#25162](https://github.com/pingcap/tidb/pull/25162)
    - Support pushing down the built-in function `json_unquote()` to TiKV [#24415](https://github.com/pingcap/tidb/issues/24415)
    - Support removing the union branch from the dual table [#25614](https://github.com/pingcap/tidb/pull/25614)
    - Support pushing down the built-in function `replace()` to TiFlash [#25565](https://github.com/pingcap/tidb/pull/25565)
    - Support pushing down the built-in functions `unix_timestamp()`, `concat()`, `year()`, `day()`, `datediff()`, `datesub()`, and `concat_ws()` to TiFlash [#25564](https://github.com/pingcap/tidb/pull/25564)
    - Optimize the aggregate operator's cost factor [#25241](https://github.com/pingcap/tidb/pull/25241)
    - Support pushing down the `Limit` operator to TiFlash [#25159](https://github.com/pingcap/tidb/pull/25159)
    - Support pushing down the built-in function `str_to_date` to TiFlash [#25148](https://github.com/pingcap/tidb/pull/25148)
    - Allow the MPP outer join to choose the build table based on the table row count [#25142](https://github.com/pingcap/tidb/pull/25142)
    - Support pushing down the built-in functions `left()`, `right()`, and `abs()` to TiFlash [#25133](https://github.com/pingcap/tidb/pull/25133)
    - Support pushing down the Broadcast Cartesian join to TiFlash [#25106](https://github.com/pingcap/tidb/pull/25106)
    - Support pushing down the `Union All` operator to TiFlash [#25051](https://github.com/pingcap/tidb/pull/25051)
    - Support balancing the MPP query workload among different TiFlash nodes based on Regions [#24724](https://github.com/pingcap/tidb/pull/24724)
    - Support invalidating stale Regions in the cache after the MPP query is executed [#24432](https://github.com/pingcap/tidb/pull/24432)
    - Improve the MySQL compatibility of the built-in function `str_to_date` for the format specifiers `%b/%M/%r/%T` [#25767](https://github.com/pingcap/tidb/pull/25767)

+ TiKV

    - Limit the TiCDC sink's memory consumption [#10305](https://github.com/tikv/tikv/pull/10305)
    - Add the memory-bounded upper limit for the TiCDC old value cache [#10313](https://github.com/tikv/tikv/pull/10313)

+ PD

    - Update TiDB Dashboard to v2021.06.15.1 [#3798](https://github.com/pingcap/pd/pull/3798)

+ TiFlash

    - Support casting the `STRING` type to the `DOUBLE` type
    - Support the `STR_TO_DATE()` function
    - Optimize the non-joined data in right outer join using multiple threads
    - Support the Cartesian join
    - Support the `LEFT()` and `RIGHT()` functions
    - Support automatically invalidating stale Regions in MPP queries
    - Support the `ABS()` function

+ Tools

    + TiCDC

        - Refine gRPC's reconnection logic and increase the KV client's throughput [#1586](https://github.com/pingcap/tiflow/issues/1586) [#1501](https://github.com/pingcap/tiflow/issues/1501#issuecomment-820027078) [#1682](https://github.com/pingcap/tiflow/pull/1682) [#1393](https://github.com/pingcap/tiflow/issues/1393) [#1847](https://github.com/pingcap/tiflow/pull/1847) [#1905](https://github.com/pingcap/tiflow/issues/1905) [#1904](https://github.com/pingcap/tiflow/issues/1904)
        - Make the sorter I/O errors more user-friendly
