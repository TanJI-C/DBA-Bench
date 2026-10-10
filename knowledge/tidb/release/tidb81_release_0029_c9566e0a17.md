# TiDB 2.0.11 release fixes for TiDB and TiKV

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-2.0.11.md`
- Source Title: `TiDB 2.0.11 Release Notes`
- Source Heading Path: `TiDB 2.0.11 Release Notes | TiDB 2.0.11 Release Notes > TiDB | TiDB 2.0.11 Release Notes > TiKV`
- Source Line Ranges: `5-20`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`
- Topic Tags: `release-notes`, `compatibility`, `stability`, `error-handling`, `mysql-compatibility`, `admin-check-table`, `add-index`, `prefix-index`, `update`, `region-merge`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0029_c9566e0a17`
- Source ID: `tidb-docs-8.1:releases/release-2.0.11.md#tidb-2-0-11-release-notes`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `09ba564f53c532a7d64661167028a8d8052964079af29f37fa5a498962d23a7c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-2.0.11#tidb-2-0-11-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-2.0.11.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 2.0.11 release-note fixes related to compatibility, stability, PD abnormal condition handling, MySQL-compatible Rename behavior, ADMIN CHECK TABLE during ADD INDEX, prefix index range, UPDATE panic after adding columns, or TiKV Region merge issues.
- Retrieval Keywords: TiDB 2.0.11 Release Notes, TiDB Ansible 2.0.11, PD is in an abnormal condition, Rename operation on a table, not compatible with that in MySQL, ADMIN CHECK TABLE, ADD INDEX, prefix index range is incorrect, UPDATE statement panic, columns are added, TiKV Region merge
- Follow-up Guidance: The source also states that TiDB Ansible 2.0.11 was released and that this release improved system compatibility and stability compared with TiDB 2.0.10.
- Classification Note: This is a self-managed release-notes chunk covering fixes in shared components, specifically TiDB and TiKV, within the TiDB 2.0.11 release.

## Official Source Content

# TiDB 2.0.11 Release Notes

On January 03, 2019, TiDB 2.0.11 is released. The corresponding TiDB Ansible 2.0.11 is also released. Compared with TiDB 2.0.10, this release has great improvement in system compatibility and stability.
## TiDB

- Fix the issue that the error is not handled properly when PD is in an abnormal condition [#8764](https://github.com/pingcap/tidb/pull/8764)
- Fix the issue that the `Rename` operation on a table in TiDB is not compatible with that in MySQL [#8809](https://github.com/pingcap/tidb/pull/8809)
- Fix the issue that the error message is wrongly reported when the `ADMIN CHECK TABLE` operation is performed in the process of executing the `ADD INDEX` statement [#8750](https://github.com/pingcap/tidb/pull/8750)
- Fix the issue that the prefix index range is incorrect in some cases [#8877](https://github.com/pingcap/tidb/pull/8877)
- Fix the panic issue of the `UPDATE` statement when columns are added in some cases [#8904](https://github.com/pingcap/tidb/pull/8904)
## TiKV

- Fix two issues about Region merge [#4003](https://github.com/tikv/tikv/pull/4003), [#4004](https://github.com/tikv/tikv/pull/4004)
