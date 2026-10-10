# PD changes in TiDB 2.0 RC3

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-2.0-rc.3.md`
- Source Title: `TiDB 2.0 RC3 Release Notes`
- Source Heading Path: `TiDB 2.0 RC3 Release Notes > PD`
- Source Line Ranges: `30-37`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: none
- Topic Tags: `release-notes`, `region-merge`, `scheduling`, `leader-balance`, `replica-management`, `abnormal-regions`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0023_8a61baf58f`
- Source ID: `tidb-docs-8.1:releases/release-2.0-rc.3.md#pd`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `917c516b99c6275a26c93174d403b1fbd7bb69cb416d5ee581c91de7dc872222`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-2.0-rc.3#pd
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-2.0-rc.3.md

## Retrieval Guidance

- Use When: Use this chunk when looking for PD 2.0 RC3 release-note items about Region Merge, replica scheduling behavior, leader balance scheduling, or abnormal Region statistics.
- Retrieval Keywords: PD 2.0 RC3, Region Merge, merge empty Regions, small Regions after deleting data, pending peers, adding replicas, restoring replicas, making nodes offline, frequent scheduling, empty Regions, leader balance, different labels, abnormal Regions statistics
- Follow-up Guidance: The source also notes fixes and optimizations for scheduling speed, including leader balance in scenarios of unbalanced resources within different labels.
- Classification Note: This is a PD release-notes chunk because it summarizes PD scheduling, replica management, Region Merge, and abnormal Region reporting changes in TiDB 2.0 RC3.

## Official Source Content

## PD

- Support Region Merge, to merge empty Regions or small Regions after deleting data
- Ignore the nodes that have a lot of pending peers during adding replicas, to improve the speed of restoring replicas or making nodes offline
- Fix the frequent scheduling issue caused by a large number of empty Regions
- Optimize the scheduling speed of leader balance in scenarios of unbalanced resources within different labels
- Add more statistics about abnormal Regions
