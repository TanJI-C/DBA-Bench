# Bug fixes for TiCDC, BR, Dumpling, and TiDB Binlog

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.1.1.md`
- Source Title: `TiDB 6.1.1 Release Notes`
- Source Heading Path: `TiDB 6.1.1 Release Notes > Bug fixes`
- Source Line Ranges: `155-178`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `ticdc`, `br`, `dumpling`, `ecosystem`
- Topic Tags: `bug-fixes`, `changefeed`, `redo-log`, `sync-point`, `rawkv`, `s3`, `ipv6`, `binlog`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0309_ccb3520bdc`
- Source ID: `tidb-docs-8.1:releases/release-6.1.1.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `dea6d26555414ba0580689260bb43d6c73e6070c55170be5fbeacd1ed70dbd72`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.1.1#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.1.1.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 6.1.1 bug fixes for TiCDC, BR, Dumpling, or TiDB Binlog related to changefeed behavior, sync-point, redo log, RawKV restore, S3 rate limiting, IPv6 support, or gzip compression.
- Retrieval Keywords: TiDB 6.1.1 bug fixes, TiCDC wrong maximum compatible version number, cdc server panic before it fully starts, ddl sink panic when the changefeed sync-point is enabled, changefeed is stuck when sync-point is enabled, changefeed API does not work properly after the cdc server restarts, black hole sink data race, enable-old-value = false, redo log feature data consistency issue, writing redo events asynchronously, MySQL sink cannot connect to IPv6 addresses, BR ErrRestoreTableIDMismatch RawKV mode, S3 rate limiting in large cluster backup, incorrect backup time in the summary log, Dumpling GetDSN does not support IPv6, Drainer cannot send requests correctly to Pump, compressor set to gzip
- Follow-up Guidance: The source also includes BR, Dumpling, and TiDB Binlog fixes such as `ErrRestoreTableIDMismatch` in RawKV mode, GetDSN IPv6 support, and Drainer requests to Pump when `compressor` is set to `gzip`.
- Classification Note: This is classified as a release bug-fix chunk because the official content is a TiDB 6.1.1 release note section listing resolved issues for TiCDC and related ecosystem tools.

## Official Source Content

- Fix the wrong maximum compatible version number [#6039](https://github.com/pingcap/tiflow/issues/6039) @[hi-rustin](https://github.com/Rustin170506)
        - Fix a bug that may cause the cdc server to panic when it receives an HTTP request before it fully starts [#5639](https://github.com/pingcap/tiflow/issues/5639) @[asddongmen](https://github.com/asddongmen)
        - Fix the ddl sink panic issue when the changefeed sync-point is enabled [#4934](https://github.com/pingcap/tiflow/issues/4934) @[asddongmen](https://github.com/asddongmen)
        - Fix the issue that a changefeed is stuck in some scenarios when sync-point is enabled [#6827](https://github.com/pingcap/tiflow/issues/6827) @[hicqu](https://github.com/hicqu)
        - Fix a bug that changefeed API does not work properly after the cdc server restarts [#5837](https://github.com/pingcap/tiflow/issues/5837) @[asddongmen](https://github.com/asddongmen)
        - Fix the data race issue in the black hole sink [#6206](https://github.com/pingcap/tiflow/issues/6206) @[asddongmen](https://github.com/asddongmen)
        - Fix the TiCDC panic issue when you set `enable-old-value = false` [#6198](https://github.com/pingcap/tiflow/issues/6198) @[hi-rustin](https://github.com/Rustin170506)
        - Fix the data consistency issue when the redo log feature is enabled [#6189](https://github.com/pingcap/tiflow/issues/6189) [#6368](https://github.com/pingcap/tiflow/issues/6368) [#6277](https://github.com/pingcap/tiflow/issues/6277) [#6456](https://github.com/pingcap/tiflow/issues/6456) [#6695](https://github.com/pingcap/tiflow/issues/6695) [#6764](https://github.com/pingcap/tiflow/issues/6764) [#6859](https://github.com/pingcap/tiflow/issues/6859) @[asddongmen](https://github.com/asddongmen)
        - Fix poor redo log performance by writing redo events asynchronously [#6011](https://github.com/pingcap/tiflow/issues/6011) @[CharlesCheung96](https://github.com/CharlesCheung96)
        - Fix the issue that the MySQL sink cannot connect to IPv6 addresses [#6135](https://github.com/pingcap/tiflow/issues/6135) @[hi-rustin](https://github.com/Rustin170506)

    + Backup & Restore (BR)

        - Fix a bug that BR reports `ErrRestoreTableIDMismatch` in RawKV mode [#35279](https://github.com/pingcap/tidb/issues/35279) @[3pointer](https://github.com/3pointer)
        - Adjust the backup data directory structure to fix backup failure caused by S3 rate limiting in large cluster backup [#30087](https://github.com/pingcap/tidb/issues/30087) @[MoCuishle28](https://github.com/MoCuishle28)
        - Fix incorrect backup time in the summary log [#35553](https://github.com/pingcap/tidb/issues/35553) @[ixuh12](https://github.com/ixuh12)

    + Dumpling

        - Fix the issue that GetDSN does not support IPv6 [#36112](https://github.com/pingcap/tidb/issues/36112) @[D3Hunter](https://github.com/D3Hunter)

    + TiDB Binlog

        - Fix a bug that Drainer cannot send requests correctly to Pump when `compressor` is set to `gzip` [#1152](https://github.com/pingcap/tidb-binlog/issues/1152) @[lichunzhu](https://github.com/lichunzhu)
