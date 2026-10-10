# Deprecated features in TiDB 8.0.0

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-8.0.0.md`
- Source Title: `TiDB 8.0.0 Release Notes`
- Source Heading Path: `TiDB 8.0.0 Release Notes > Deprecated features`
- Source Line Ranges: `360-366`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `lightning`, `sql`
- Topic Tags: `deprecated-features`, `tls`, `transaction-retry`, `conflict-detection`, `plan-bindings`, `release-notes`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0583_dff2e3b224`
- Source ID: `tidb-docs-8.1:releases/release-8.0.0.md#deprecated-features`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `90721f19eb6bfdb4558b368b60cc1de9f430f9ab1b9dd5027e182afbd1201e86`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-8.0.0#deprecated-features
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-8.0.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for features deprecated in TiDB 8.0.0, including transaction retry behavior, supported TLS protocols, TiDB Lightning conflict detection, and execution plan binding evolution.
- Retrieval Keywords: TiDB 8.0.0 deprecated features, tidb_disable_txn_auto_retry deprecated, automatic retries of optimistic transactions, Pessimistic transaction mode, TLSv1.0 TLSv1.1 no longer supported, TLSv1.2 TLSv1.3, TiDB Lightning old version of conflict detection deprecated, conflict.strategy, duplicate-resolution will be removed in a future release, auto-evolution of execution plan bindings, baseline evolution
- Follow-up Guidance: The source notes alternatives for optimistic transaction conflicts: capture the error and retry transactions in your application, or use the Pessimistic transaction mode instead.
- Classification Note: This is classified as a release deprecation chunk because the official content lists deprecated or no-longer-supported features and planned behavior changes introduced in TiDB 8.0.0.

## Official Source Content

## Deprecated features

- Starting from v8.0.0, the [`tidb_disable_txn_auto_retry`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_disable_txn_auto_retry) system variable is deprecated, and TiDB no longer supports automatic retries of optimistic transactions. As an alternative, when encountering optimistic transaction conflicts, you can capture the error and retry transactions in your application, or use the [Pessimistic transaction mode](https://docs.pingcap.com/tidb/stable/pessimistic-transaction) instead.
- Starting from v8.0.0, TiDB no longer supports the TLSv1.0 and TLSv1.1 protocols. You must upgrade TLS to TLSv1.2 or TLSv1.3.
- Starting from v8.0.0, TiDB Lightning deprecates the [old version of conflict detection](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-physical-import-mode-usage#the-old-version-of-conflict-detection-deprecated-in-v800) strategy for the physical import mode, and enables you to control the conflict detection strategy for both logical and physical import modes via the [`conflict.strategy`](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration) parameter. The [`duplicate-resolution`](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration) parameter for the old version of conflict detection will be removed in a future release.
- It is planned to redesign [the auto-evolution of execution plan bindings](https://docs.pingcap.com/tidb/stable/sql-plan-management#baseline-evolution) in subsequent releases, and the related variables and behavior will change.
