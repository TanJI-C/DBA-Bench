# TiCDC unsupported scenarios and partial support limits

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-overview.md`
- Source Title: `TiCDC Overview`
- Source Heading Path: `TiCDC Overview > Unsupported scenarios`
- Source Line Ranges: `144-152`
- Source Scope: `all`
- Primary Component: `ticdc`
- Related Components: `br`, `lightning`, `sql`, `tidb`, `tikv`
- Topic Tags: `unsupported-scenarios`, `rawkv`, `sequence`, `ddl`, `dml`, `br-recovery`, `physical-import`, `large-transactions`, `replication-limits`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0775_238635ee10`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-overview.md#unsupported-scenarios`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `cdc28c2f0f5d353bd681994ab7e17ffeb5674e14a6f6ed056d32f4277588a628`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-overview#unsupported-scenarios
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-overview.md

## Retrieval Guidance

- Use When: Use this chunk when checking whether a TiCDC replication scenario is unsupported or only partially supported, including RawKV-only TiKV, SEQUENCE-related behavior, BR recovery, TiDB Lightning physical import, or large upstream transactions.
- Retrieval Keywords: Unsupported scenarios, TiCDC Overview, RawKV, TiKV cluster that uses RawKV alone, CREATE SEQUENCE, SEQUENCE function, TiCDC ignores SEQUENCE DDL operations/functions performed upstream, DML operations using SEQUENCE functions can be correctly replicated, BR data recovery, TiDB Lightning physical import, replicated by TiCDC, replication using TiCDC stall or even stop after data restore, large transactions in the upstream, TiCDC only partially supports
- Follow-up Guidance: The source points to the TiCDC FAQ for details about large transaction replication risks and for why replication can stall or stop after BR recovery or TiDB Lightning physical import from upstream.
- Classification Note: This is reference content because it enumerates unsupported TiCDC scenarios and partial support limits rather than providing a procedure.

## Official Source Content

## Unsupported scenarios

Currently, the following scenarios are not supported:

- A TiKV cluster that uses RawKV alone.
- The [`CREATE SEQUENCE` DDL operation](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-sequence) and the [`SEQUENCE` function](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-sequence#sequence-function) in TiDB. When the upstream TiDB uses `SEQUENCE`, TiCDC ignores `SEQUENCE` DDL operations/functions performed upstream. However, DML operations using `SEQUENCE` functions can be correctly replicated.
- Currently, performing [BR data recovery](https://docs.pingcap.com/tidb/stable/br/backup-and-restore-overview) and [TiDB Lightning physical import](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-physical-import-mode) imports on tables and databases that are being replicated by TiCDC is not supported. For more information, see [Why does replication using TiCDC stall or even stop after data restore using TiDB Lightning and BR from upstream](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-faq#why-does-replication-using-ticdc-stall-or-even-stop-after-data-restore-using-tidb-lightning-physical-import-mode-and-br-from-upstream).

TiCDC only partially supports scenarios involving large transactions in the upstream. For details, refer to the [TiCDC FAQ](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-faq#does-ticdc-support-replicating-large-transactions-is-there-any-risk), where you can find details on whether TiCDC supports replicating large transactions and any associated risks.
