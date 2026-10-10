# Compatibility changes for TiDB and TiKV

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-4.0.14.md`
- Source Title: `TiDB 4.0.14 Release Notes`
- Source Heading Path: `TiDB 4.0.14 Release Notes > Compatibility changes`
- Source Line Ranges: `12-23`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `dashboard`
- Topic Tags: `default value`, `system variable`, `security vulnerability`, `region merge`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0141_b15e96e073`
- Source ID: `tidb-docs-8.1:releases/release-4.0.14.md#compatibility-changes`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e6d587abe7e3900df4ab7f27cbbd58cddb1a8f046510553c289d80eed238f6eb`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-4.0.14#compatibility-changes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-4.0.14.md

## Retrieval Guidance

- Use When: Use this chunk when searching for compatibility changes in TiDB 4.0.14 involving default values, system variables, Grafana security fixes, or TiKV Region merge settings.
- Retrieval Keywords: Compatibility changes, tidb_multi_statement_mode, default value WARN to OFF, multi-statement feature of your client library, Grafana dashboard v6.1.16 to v7.5.7, security vulnerabilities, tidb_stmt_summary_max_stmt_count, default value 200 to 3000, merge-check-tick-interval, default value 10 to 2, speed up the Region merge process
- Follow-up Guidance: The chunk also points to the documentation on `tidb_multi_statement_mode` and a Grafana blog post for more details.
- Classification Note: This is classified as configuration because the official content focuses on changed default values and compatibility-affecting settings in TiDB and TiKV.

## Official Source Content

## Compatibility changes

+ TiDB

    - Change the default value of `tidb_multi_statement_mode` from `WARN` to `OFF` in v4.0. It is recommended to use the multi-statement feature of your client library instead. See [the documentation on `tidb_multi_statement_mode`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_multi_statement_mode-new-in-v4011) for details. [#25749](https://github.com/pingcap/tidb/pull/25749)
    - Upgrade Grafana dashboard from v6.1.16 to v7.5.7 to solve two security vulnerabilities. See the [Grafana blog post](https://grafana.com/blog/2020/06/03/grafana-6.7.4-and-7.0.2-released-with-important-security-fix/) for details.
    - Change the default value of the `tidb_stmt_summary_max_stmt_count` variable from `200` to `3000` [#25872](https://github.com/pingcap/tidb/pull/25872)

+ TiKV

    - Change the default value of `merge-check-tick-interval` from `10` to `2` to speed up the Region merge process [#9676](https://github.com/tikv/tikv/pull/9676)
