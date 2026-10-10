# Bug fixes for Lightning, Dumpling, and TiDB Binlog

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.1.1.md`
- Source Title: `TiDB 7.1.1 Release Notes`
- Source Heading Path: `TiDB 7.1.1 Release Notes > Bug fixes`
- Source Line Ranges: `142-157`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `lightning`, `dumpling`, `tidb`
- Topic Tags: `bug-fixes`, `import`, `checksum`, `disk-quota`, `logical-import`, `sql-export`, `binlog`, `pd-address`, `etcd-client`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0457_e79e736e1e`
- Source ID: `tidb-docs-8.1:releases/release-7.1.1.md#bug-fixes`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8455718f552eb5ead3f2d807493ac5bf9ea03bd2539f42a7bcd4c23539d101ab`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.1.1#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.1.1.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 7.1.1 bug fixes in TiDB Lightning, Dumpling, or TiDB Binlog related to import retries, checksum errors, disk quota, Logical Import Mode, empty --sql results, or PD address changes.
- Retrieval Keywords: TiDB 7.1.1 bug fixes Lightning Dumpling TiDB Binlog, TiDB Lightning failed connection between TiDB Lightning and PD cannot be retried, writing data to TiKV returns an out of space error, Region is unavailable error during checksum operation, experimental.allow-expression-index default value is UUID panic, disk quota might be inaccurate due to competing conditions, Logical Import Mode deleting tables downstream during import metadata not updated in time, Dumpling exits abnormally when the query result set of --sql is empty, SHOW PUMP STATUS, SHOW DRAINER STATUS, complete change of the PD address, TiDB cannot write binlogs after a complete change of the PD address, etcd client does not automatically synchronize the latest node information during initialization
- Follow-up Guidance: 
- Classification Note: This chunk is classified as a release bug-fix summary because the official content enumerates resolved issues for Lightning, Dumpling, and TiDB Binlog in TiDB 7.1.1.

## Official Source Content

- Fix the issue that the failed connection between TiDB Lightning and PD cannot be retried, improving the import success rate [#43400](https://github.com/pingcap/tidb/issues/43400) @[lichunzhu](https://github.com/lichunzhu)
        - Fix the issue that TiDB Lightning does not correctly display the error message when writing data to TiKV returns an out of space error [#44733](https://github.com/pingcap/tidb/issues/44733) @[lance6716](https://github.com/lance6716)
        - Fix the issue that the `Region is unavailable` error is reported during checksum operation [#45462](https://github.com/pingcap/tidb/issues/45462) @[D3Hunter](https://github.com/D3Hunter)
        - Fix the TiDB Lightning panic issue when `experimental.allow-expression-index` is enabled and the default value is UUID [#44497](https://github.com/pingcap/tidb/issues/44497) @[lichunzhu](https://github.com/lichunzhu)
        - Fix the issue that disk quota might be inaccurate due to competing conditions [#44867](https://github.com/pingcap/tidb/issues/44867) @[D3Hunter](https://github.com/D3Hunter)
        - Fix the issue that in Logical Import Mode, deleting tables downstream during import might cause TiDB Lightning metadata not to be updated in time [#44614](https://github.com/pingcap/tidb/issues/44614) @[dsdashun](https://github.com/dsdashun)

    + Dumpling

        - Fix the issue that Dumpling exits abnormally when the query result set of `--sql` is empty [#45200](https://github.com/pingcap/tidb/issues/45200) @[D3Hunter](https://github.com/D3Hunter)

    + TiDB Binlog

        - Fix the issue that TiDB cannot correctly query Binlog node status via `SHOW PUMP STATUS` or `SHOW DRAINER STATUS` after a complete change of the PD address [#42643](https://github.com/pingcap/tidb/issues/42643) @[lichunzhu](https://github.com/lichunzhu)
        - Fix the issue that TiDB cannot write binlogs after a complete change of the PD address [#42643](https://github.com/pingcap/tidb/issues/42643) @[lance6716](https://github.com/lance6716)
        - Fix the issue that the etcd client does not automatically synchronize the latest node information during initialization [#1236](https://github.com/pingcap/tidb-binlog/issues/1236) @[lichunzhu](https://github.com/lichunzhu)
