# Compatibility overview for Lightning logical mode, physical mode, and IMPORT INTO

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-lightning/tidb-lightning-compatibility-and-scenarios.md`
- Source Title: `Compatibility of TiDB Lightning and IMPORT INTO with TiCDC and Log Backup`
- Source Heading Path: `Compatibility of TiDB Lightning and IMPORT INTO with TiCDC and Log Backup | Compatibility of TiDB Lightning and IMPORT INTO with TiCDC and Log Backup > `IMPORT INTO` vs. TiDB Lightning | Compatibility of TiDB Lightning and IMPORT INTO with TiCDC and Log Backup > Compatibility with log backup and TiCDC | Compatibility of TiDB Lightning and IMPORT INTO with TiCDC and Log Backup > Scenarios for TiDB Lightning logical import mode`
- Source Line Ranges: `5-27`
- Source Scope: `self_managed`
- Primary Component: `lightning`
- Related Components: `br`, `ticdc`, `sql`, `tikv`
- Topic Tags: `compatibility`, `logical-import`, `physical-import`, `log-backup`, `ticdc`, `pitr`, `changefeed`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0937_f0bf005fad`
- Source ID: `tidb-docs-8.1:tidb-lightning/tidb-lightning-compatibility-and-scenarios.md#compatibility-of-tidb-lightning-and-import-into-with-ticdc-and-log-backup`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f79751fd4396f4e5c921e0c3ce5d31e021453fb20a67bc76b248ce9ff0fc207c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-compatibility-and-scenarios#compatibility-of-tidb-lightning-and-import-into-with-ticdc-and-log-backup
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-lightning/tidb-lightning-compatibility-and-scenarios.md

## Retrieval Guidance

- Use When: Use this chunk when you need the compatibility overview of TiDB Lightning logical import mode, TiDB Lightning physical import mode, and `IMPORT INTO` with log backup or TiCDC, including when logical import mode is suitable for downstream backup or replication requirements.
- Retrieval Keywords: TiDB Lightning logical import mode compatible with log backup and TiCDC, TiDB Lightning physical import mode not compatible with log backup and TiCDC, IMPORT INTO not compatible with log backup and TiCDC, IMPORT INTO vs. TiDB Lightning, Compatibility with TiDB Lightning, logical import mode, physical import mode, change logs, TiKV, log backup, TiCDC
- Follow-up Guidance: The source points to `IMPORT INTO` vs. TiDB Lightning for differences and to TiCDC compatibility with TiDB Lightning for cluster usage details.
- Classification Note: This is classified as reference because the content summarizes compatibility relationships and scenario selection guidance rather than step-by-step procedures.

## Official Source Content

# Compatibility of TiDB Lightning and IMPORT INTO with TiCDC and Log Backup

This document describes TiDB Lightning and [`IMPORT INTO`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-import-into) compatibility with [log backup](https://docs.pingcap.com/tidb/stable/br/br-pitr-guide) and [TiCDC](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-overview), as well as some special usage scenarios.
## `IMPORT INTO` vs. TiDB Lightning

[`IMPORT INTO`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-import-into) integrates with the physical import mode of TiDB Lightning, but there are some differences. See [`IMPORT INTO` vs. TiDB Lightning](https://docs.pingcap.com/tidb/stable/tidb-lightning/import-into-vs-tidb-lightning) for details.
## Compatibility with log backup and TiCDC

- TiDB Lightning [logical import mode](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-logical-import-mode) is compatible with log backup and TiCDC.

- TiDB Lightning [physical import mode](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-physical-import-mode) is not compatible with log backup and TiCDC. The reason is that physical import mode directly ingests encoded KV pairs of the source data to TiKV, causing TiKV not to generate corresponding change logs during this process. Without such change logs, the relevant data cannot be backed up via log backup and cannot be replicated by TiCDC.

- To use TiDB Lightning and TiCDC together in a cluster, see [Compatibility with TiDB Lightning](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-compatibility#compatibility-with-tidb-lightning).

- `IMPORT INTO` is not compatible with log backup and TiCDC. The reason is that `IMPORT INTO` also ingests encoded KV pairs of the source data directly to TiKV.
## Scenarios for TiDB Lightning logical import mode

If TiDB Lightning logical import mode can meet your application's performance requirements and your application requires imported tables to be backed up or replicated downstream using TiCDC, it is recommended to use TiDB Lightning logical import mode.
