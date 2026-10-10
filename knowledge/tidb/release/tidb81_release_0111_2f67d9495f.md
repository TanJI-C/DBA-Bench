# TiDB 3.0.18 release notes, improvements, and bug fixes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-3.0.18.md`
- Source Title: `TiDB 3.0.18 Release Notes`
- Source Heading Path: `TiDB 3.0.18 Release Notes | TiDB 3.0.18 Release Notes > Improvements | TiDB 3.0.18 Release Notes > Bug Fixes`
- Source Line Ranges: `5-40`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `lightning`
- Topic Tags: `release-date`, `version`, `improvements`, `bug-fixes`, `binlog`, `pump-gc`, `hashjoin`, `decimal`, `set`, `enum`, `pessimistic-locking`, `duplicate-keys`, `apply`, `union-scan`, `cached-execution-plans`, `gc-logging`, `log-file`, `binary-literals`, `hex-literals`, `switch-mode`, `tidb-backend`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0111_2f67d9495f`
- Source ID: `tidb-docs-8.1:releases/release-3.0.18.md#tidb-3-0-18-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b2e417787b0b62298bf9c7053ddd1767e18ea340a0a4f823532708ba8b3b884f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-3.0.18#tidb-3-0-18-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-3.0.18.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB 3.0.18 release date and the specific improvements or bug fixes related to TiDB Binlog, TiDB, TiKV, or TiDB Lightning in this release.
- Retrieval Keywords: TiDB 3.0.18 Release Notes, August 21, 2020, TiDB version 3.0.18, Pump GC configuration, time duration format of Go, decimal Hash function wrong HashJoin result, set enum Hash function wrong HashJoin result, duplicate keys pessimistic locking mode, Apply Union Scan wrong execution result, cached execution plans incorrectly executed in transaction, GC failure log warning level, --log-file argument does not take effect, empty binary/hex literals TiDB-backend, unexpected switch-mode call TiDB-backend, TiDB Binlog, TiDB Lightning
- Follow-up Guidance: 
- Classification Note: This is a release-notes chunk because the official content lists the release date, version, one improvement, and multiple bug fixes grouped by component for TiDB 3.0.18.

## Official Source Content

# TiDB 3.0.18 Release Notes

Release date: August 21, 2020

TiDB version: 3.0.18
## Improvements

+ Tools

    + TiDB Binlog

        - Support the time duration format of Go for the Pump GC configuration [#996](https://github.com/pingcap/tidb-binlog/pull/996)
## Bug Fixes

+ TiDB

    - Fix the issue that the wrong handling of the `decimal` type by the `Hash` function causes the wrong HashJoin result [#19185](https://github.com/pingcap/tidb/pull/19185)
    - Fix the issue that the wrong handling of the `set` and `enum` types by the `Hash` function causes the wrong HashJoin result [#19175](https://github.com/pingcap/tidb/pull/19175)
    - Fix the issue that the check for duplicate keys fails in the pessimistic locking mode [#19236](https://github.com/pingcap/tidb/pull/19236)
    - Fix the issue that the `Apply` and `Union Scan` operators cause the wrong execution result [#19297](https://github.com/pingcap/tidb/pull/19297)
    - Fix the issue that some cached execution plans are incorrectly executed in transaction [#19274](https://github.com/pingcap/tidb/pull/19274)

+ TiKV

    - Change the GC failure log from `error` to the `warning` level [#8444](https://github.com/tikv/tikv/pull/8444)

+ Tools

    + TiDB Lightning

        - Fix the issue that the `--log-file` argument does not take effect [#345](https://github.com/pingcap/tidb-lightning/pull/345)
        - Fix the syntax error on empty binary/hex literals when using TiDB-backend [#357](https://github.com/pingcap/tidb-lightning/pull/357)
        - Fix the unexpected `switch-mode` call when using TiDB-backend [#368](https://github.com/pingcap/tidb-lightning/pull/368)
