# Offline package update and deprecated features

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.6.0.md`
- Source Title: `TiDB 7.6.0 Release Notes`
- Source Heading Path: `TiDB 7.6.0 Release Notes > Offline package changes | TiDB 7.6.0 Release Notes > Deprecated features`
- Source Line Ranges: `311-320`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `sql`, `tidb`, `tiproxy`
- Topic Tags: `offline-package`, `binary-package`, `deprecation`, `tls`, `plan-management`, `transaction-retry`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0566_e7a8a28e8a`
- Source ID: `tidb-docs-8.1:releases/release-7.6.0.md#offline-package-changes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0acbcc93858d73c1b50de64929e085bf768534b90363b9b017967d8400ae3891`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.6.0#offline-package-changes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.6.0.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 7.6.0 offline package changes or deprecated features related to TiProxy, TLS protocols, baseline evolution, and tidb_disable_txn_auto_retry.
- Retrieval Keywords: TiDB 7.6.0 offline package changes, TiDB-community-server binary-package, tiproxy-{version}-linux-{arch}.tar.gz, TiProxy, deprecated features, TLSv1.0, TLSv1.1, TLSv1.2, TLSv1.3, baseline evolution, sql-plan-management, tidb_disable_txn_auto_retry, automatic retries of optimistic transactions
- Follow-up Guidance: The source states that starting from v7.6.0 the TiDB-community-server binary package includes the TiProxy installation package, and that the listed deprecated features target removal or deprecation in v8.0.0.
- Classification Note: This is a release-note deprecation and packaging update because the official content describes an offline binary-package inclusion change and features marked deprecated.

## Official Source Content

## Offline package changes

Starting from v7.6.0, the `TiDB-community-server` [binary-package](https://docs.pingcap.com/tidb/stable/binary-package) now includes `tiproxy-{version}-linux-{arch}.tar.gz`, which is the installation package for the proxy component [TiProxy](https://docs.pingcap.com/tidb/stable/tiproxy/tiproxy-overview).
## Deprecated features

* Support for the TLSv1.0 and TLSv1.1 protocols is deprecated in TiDB v7.6.0 and will be removed in v8.0.0. Please upgrade to TLSv1.2 or TLSv1.3.
* The [baseline evolution](https://docs.pingcap.com/tidb/stable/sql-plan-management#baseline-evolution) feature for execution plans will be deprecated in TiDB v8.0.0. The equivalent functionality will be redesigned in the subsequent versions.
* The [`tidb_disable_txn_auto_retry`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_disable_txn_auto_retry) system variable will be deprecated in TiDB v8.0.0. After that, TiDB will no longer support automatic retries of optimistic transactions.
