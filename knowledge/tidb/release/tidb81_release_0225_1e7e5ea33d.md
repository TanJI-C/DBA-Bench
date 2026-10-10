# Release overview, compatibility changes, and feature enhancements

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.1.1.md`
- Source Title: `TiDB 5.1.1 Release Notes`
- Source Heading Path: `TiDB 5.1.1 Release Notes | TiDB 5.1.1 Release Notes > Compatibility changes | TiDB 5.1.1 Release Notes > Feature enhancements`
- Source Line Ranges: `5-36`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `dashboard`, `tiflash`
- Topic Tags: `release-notes`, `compatibility`, `default-values`, `privileges`, `oidc`, `sso`, `dashboard`, `tiflash`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0225_1e7e5ea33d`
- Source ID: `tidb-docs-8.1:releases/release-5.1.1.md#tidb-5-1-1-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9b8eafdfdb3693bb7415087139597b66600c0788332961502eca85097d42d122`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.1.1#tidb-5-1-1-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.1.1.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 5.1.1 compatibility changes, default-value changes, privilege requirements for system tables, or feature enhancements in TiDB Dashboard and TiFlash.
- Retrieval Keywords: TiDB 5.1.1 Release Notes, Compatibility changes, Feature enhancements, tidb_multi_statement_mode, default value OFF, tidb_stmt_summary_max_stmt_count, table_storage_stats, information_schema.user_privileges, mysql.user, information_schema.cluster_hardware, information_schema.cluster_info, information_schema.cluster_load, information_schema.cluster_systeminfo, information_schema.cluster_log, information_schema.cluster_config, SUPER privilege, SELECT privilege, CONFIG privilege, PROCESS privilege, TiDB Dashboard, OIDC SSO, Okta, Auth0, TiFlash, HAVING() function, DAG requests
- Follow-up Guidance: The source also states that TiDB Dashboard supports OIDC-compatible SSO services such as Okta and Auth0, and TiFlash supports the HAVING() function in DAG requests.
- Classification Note: This is a release-notes chunk covering compatibility changes and feature enhancements for TiDB 5.1.1 across shared components including TiDB, Dashboard, and TiFlash.

## Official Source Content

# TiDB 5.1.1 Release Notes

Release Date: July 30, 2021

TiDB version: 5.1.1
## Compatibility changes

+ TiDB

    - For TiDB clusters upgrade from v4.0 to v5.1, the default value of `tidb_multi_statement_mode` is `OFF`. It is recommended to use the multi-statement feature of your client library instead. See [the documentation on `tidb_multi_statement_mode`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_multi_statement_mode-new-in-v4011) for details. [#25751](https://github.com/pingcap/tidb/pull/25751)
    - Change the default value of the `tidb_stmt_summary_max_stmt_count` variable from `200` to `3000` [#25874](https://github.com/pingcap/tidb/pull/25874)
    - Require the `SUPER` privilege to access the `table_storage_stats` table [#26352](https://github.com/pingcap/tidb/pull/26352)
    - Require the `SELECT` privilege on `mysql.user` to access the `information_schema.user_privileges` table to show other user's privileges [#26311](https://github.com/pingcap/tidb/pull/26311)
    - Require the `CONFIG` privilege to access the `information_schema.cluster_hardware` table [#26297](https://github.com/pingcap/tidb/pull/26297)
    - Require the `PROCESS` privilege to access the `information_schema.cluster_info` table [#26297](https://github.com/pingcap/tidb/pull/26297)
    - Require the `PROCESS` privilege to access the `information_schema.cluster_load` table [#26297](https://github.com/pingcap/tidb/pull/26297)
    - Require the `PROCESS` privilege to access the `information_schema.cluster_systeminfo` table [#26297](https://github.com/pingcap/tidb/pull/26297)
    - Require the `PROCESS` privilege to access the `information_schema.cluster_log` table [#26297](https://github.com/pingcap/tidb/pull/26297)
    - Require the `CONFIG` privilege to access the `information_schema.cluster_config` table [#26150](https://github.com/pingcap/tidb/pull/26150)
## Feature enhancements

+ TiDB Dashboard

    - Support OIDC SSO. By setting the OIDC-compatible SSO services (such as Okta and Auth0), users can log into TiDB Dashboard without entering the SQL password. [#3883](https://github.com/tikv/pd/pull/3883)

+ TiFlash

    - Support the `HAVING()` function in DAG requests
