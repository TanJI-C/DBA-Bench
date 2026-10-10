# Compatibility changes in other areas

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.6.0.md`
- Source Title: `TiDB 6.6.0 Release Notes`
- Source Heading Path: `TiDB 6.6.0 Release Notes > Compatibility changes > Others`
- Source Line Ranges: `420-426`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tikv`, `br`, `tidb`
- Topic Tags: `compatibility`, `dynamic-configuration`, `limit-clause`, `restore-version-support`, `partitioned-tables`, `column-type-changes`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0423_37c88166ad`
- Source ID: `tidb-docs-8.1:releases/release-6.6.0.md#others`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6c482c72f0b7c222b8baaf49e8faf6240d7019538d59049aceba0e3962dc6a4f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.6.0#others
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.6.0.md

## Retrieval Guidance

- Use When: Use this chunk when checking TiDB 6.6.0 compatibility changes related to dynamic configuration, LIMIT clause behavior, BR restore version support, or partitioned table column type modifications.
- Retrieval Keywords: TiDB 6.6.0 compatibility changes others, store-io-pool-size, dynamically modifying store-io-pool-size, Remove the limit on LIMIT clauses, BR does not support restoring data to clusters earlier than v6.1.0, starting from v6.6.0 BR restore version support, TiDB no longer supports modifying column types on partitioned tables, partitioned tables column type correctness issues
- Follow-up Guidance: The source states that starting from v6.6.0, BR does not support restoring data to clusters earlier than v6.1.0, and TiDB no longer supports modifying column types on partitioned tables.
- Classification Note: This is classified as a release compatibility chunk because it lists behavior and support changes introduced in TiDB 6.6.0 across TiKV, BR, and TiDB.

## Official Source Content

### Others

- Support dynamically modifying [`store-io-pool-size`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#store-io-pool-size-new-in-v530). This facilitates more flexible TiKV performance tuning.
- Remove the limit on `LIMIT` clauses, thus improving the execution performance.
- Starting from v6.6.0, BR does not support restoring data to clusters earlier than v6.1.0.
- Starting from v6.6.0, TiDB no longer supports modifying column types on partitioned tables because of potential correctness issues.
