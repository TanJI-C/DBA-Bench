# Bug fixes for TiDB Lightning and TiDB Binlog

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.1.2.md`
- Source Title: `TiDB 7.1.2 Release Notes`
- Source Heading Path: `TiDB 7.1.2 Release Notes > Bug fixes`
- Source Line Ranges: `211-220`
- Source Scope: `self_managed`
- Primary Component: `lightning`
- Related Components: `pd`, `tidb`
- Topic Tags: `bug-fixes`, `import`, `csv`, `checksum`, `auto-id`, `row-id`, `pd-topology`, `binlog`, `drainer`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0463_b051afd19a`
- Source ID: `tidb-docs-8.1:releases/release-7.1.2.md#bug-fixes`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `665878a3644a012a9b0a39f7d96b02c0d92f04179685479566b7ac62d860f90a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.1.2#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.1.2.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 7.1.2 bug fixes in TiDB Lightning or TiDB Binlog involving import row ID handling, checksum behavior, PD address or topology changes, CSV import panic, or Drainer exiting on very large transactions.
- Retrieval Keywords: TiDB 7.1.2 bug fixes, TiDB Lightning AUTO_ID_CACHE=1 wrong row_id, NEXT_GLOBAL_ROW_ID wrong data type, checksum = "optional" still reports errors, data import fails when PD cluster address changes, TiDB Lightning fails to start when PD topology is changed, route might panic when importing CSV data, TiDB Binlog Drainer exits transaction greater than 1 GB
- Follow-up Guidance: 
- Classification Note: This chunk is classified as a release bug-fix summary because it enumerates fixed issues for TiDB Lightning and TiDB Binlog in TiDB 7.1.2.

## Official Source Content

- Fix the issue that when importing a table with `AUTO_ID_CACHE=1`, a wrong `row_id` is assigned [#46100](https://github.com/pingcap/tidb/issues/46100) @[D3Hunter](https://github.com/D3Hunter)
        - Fix the issue that the data type is wrong when saving `NEXT_GLOBAL_ROW_ID` [#45427](https://github.com/pingcap/tidb/issues/45427) @[lyzx2001](https://github.com/lyzx2001)
        - Fix the issue that checksum still reports errors when `checksum = "optional"` [#45382](https://github.com/pingcap/tidb/issues/45382) @[lyzx2001](https://github.com/lyzx2001)
        - Fix the issue that data import fails when the PD cluster address changes [#43436](https://github.com/pingcap/tidb/issues/43436) @[lichunzhu](https://github.com/lichunzhu)
        - Fix the issue that TiDB Lightning fails to start when PD topology is changed [#46688](https://github.com/pingcap/tidb/issues/46688) @[lance6716](https://github.com/lance6716)
        - Fix the issue that route might panic when importing CSV data [#43284](https://github.com/pingcap/tidb/issues/43284) @[lyzx2001](https://github.com/lyzx2001)

    + TiDB Binlog

        - Fix the issue that Drainer exits when transporting a transaction greater than 1 GB [#28659](https://github.com/pingcap/tidb/issues/28659) @[jackysp](https://github.com/jackysp)
