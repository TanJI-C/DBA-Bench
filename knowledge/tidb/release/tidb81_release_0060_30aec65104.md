# PD and TiKV fixes in TiDB 2.1.12

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-2.1.12.md`
- Source Title: `TiDB 2.1.12 Release Notes`
- Source Heading Path: `TiDB 2.1.12 Release Notes > PD | TiDB 2.1.12 Release Notes > TiKV`
- Source Line Ranges: `36-43`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `pd`, `tikv`
- Topic Tags: `release-notes`, `leader-election`, `region-availability`, `leader-transfer`, `power-failure`, `data-loss`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0060_30aec65104`
- Source ID: `tidb-docs-8.1:releases/release-2.1.12.md#pd`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `edea5c46cafd9889ba366083c72daaefd0dda76fdfc62aad7bba4082adb96986`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-2.1.12#pd
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-2.1.12.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 2.1.12 release fixes in PD and TiKV involving etcd leader election, Region availability during leader transfer, or data loss after abnormal power failure while receiving snapshots.
- Retrieval Keywords: TiDB 2.1.12 Release Notes, PD, TiKV, etcd leader election is blocked, leader election, Regions are not available, leader transfer process, power fails abnormally, loses data, delayed data flush to the disk, receiving snapshots
- Follow-up Guidance: The source separates one fix under PD and two fixes under TiKV in the TiDB 2.1.12 release notes.
- Classification Note: This is classified as a shared release chunk because the official content covers both PD and TiKV fixes rather than TiDB alone.

## Official Source Content

## PD

- Fix the issue that etcd leader election is blocked in extreme conditions [#1576](https://github.com/pingcap/pd/pull/1576)
## TiKV

- Fix the issue that Regions are not available during the leader transfer process in extreme conditions [#4799](https://github.com/tikv/tikv/pull/4734)
- Fix the issue that TiKV loses data when the power of the machine fails abnormally, caused by delayed data flush to the disk when receiving snapshots [#4850](https://github.com/tikv/tikv/pull/4850)
