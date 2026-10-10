# TiDB 2.0.2 release notes and component fixes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-2.0.2.md`
- Source Title: `TiDB 2.0.2 Release Notes`
- Source Heading Path: `TiDB 2.0.2 Release Notes | TiDB 2.0.2 Release Notes > TiDB | TiDB 2.0.2 Release Notes > PD | TiDB 2.0.2 Release Notes > TiKV`
- Source Line Ranges: `5-30`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `pd`, `tikv`
- Topic Tags: `release-notes`, `stability`, `bug-fixes`, `scheduler`, `raft`, `binlog`, `grpc`, `leader-election`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0030_241cc291b4`
- Source ID: `tidb-docs-8.1:releases/release-2.0.2.md#tidb-2-0-2-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2065b29d439771843781f17a831c2b3658d538f3b1ea2a59cac8027d21fff286`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-2.0.2#tidb-2-0-2-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-2.0.2.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB 2.0.2 release notes that summarize stability improvements and specific fixes in TiDB, PD, and TiKV.
- Retrieval Keywords: TiDB 2.0.2 Release Notes, 2.0.2 release notes, system stability, Decimal division expression pushdown, USE INDEX Delete statement, shard_row_id_bits Auto-Increment, Binlog timeout mechanism, balance leader scheduler disconnected nodes, transfer leader operator timeout 10s, label scheduler unhealthy Regions, evict leader scheduler, Raft log is not printed, gRPC related parameters, leader election timeout range, obsolete learner is not deleted, snapshot intermediate file is mistakenly deleted
- Follow-up Guidance: The content groups the fixes under TiDB, PD, and TiKV and identifies the affected features and schedulers for each component.
- Classification Note: This is classified as a release chunk because the official content is the TiDB 2.0.2 release notes listing component-specific bug fixes and behavior changes for TiDB, PD, and TiKV.

## Official Source Content

# TiDB 2.0.2 Release Notes

On May 21, 2018, TiDB 2.0.2 is released. Compared with TiDB 2.0.1, this release has great improvement in system stability.
## TiDB

- Fix the issue of pushing down the Decimal division expression
- Support using the `USE INDEX` syntax in the `Delete` statement
- Forbid using the `shard_row_id_bits` feature in columns with `Auto-Increment`
- Add the timeout mechanism for writing Binlog
## PD

- Make the balance leader scheduler filter the disconnected nodes
- Modify the timeout of the transfer leader operator to 10s
- Fix the issue that the label scheduler does not schedule when the cluster Regions are in an unhealthy state
- Fix the improper scheduling issue of `evict leader scheduler`
## TiKV

- Fix the issue that the Raft log is not printed
- Support configuring more gRPC related parameters
- Support configuring the timeout range of leader election
- Fix the issue that the obsolete learner is not deleted
- Fix the issue that the snapshot intermediate file is mistakenly deleted
