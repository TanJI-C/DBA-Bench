# TiDB 3.0.2 fixes for TiKV, PD, and tools

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-3.0.2.md`
- Source Title: `TiDB 3.0.2 Release Notes`
- Source Heading Path: `TiDB 3.0.2 Release Notes > TiKV | TiDB 3.0.2 Release Notes > PD | TiDB 3.0.2 Release Notes > Tools`
- Source Line Ranges: `97-127`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tikv`, `pd`, `lightning`
- Topic Tags: `release-notes`, `raft-log`, `panic-logging`, `pessimistic-transaction`, `deadlock-detector`, `gc`, `scatter-region`, `pd-ctl`, `binlog`, `lightning`, `configuration-check`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0115_c47cea45d4`
- Source ID: `tidb-docs-8.1:releases/release-3.0.2.md#tikv`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `fa11d47391be7bccc6a8c50cbcd3d8d49aa7990bf30da4b8f82b16e24529a827`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-3.0.2#tikv
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-3.0.2.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 3.0.2 release-note fixes for TiKV, PD, or tools such as Raft log panic handling, pessimistic transaction behavior, deadlock detector performance, Scatter Region scheduling, pd-ctl operations, Binlog configuration checks, or Lightning checksum and configuration-check behavior.
- Retrieval Keywords: TiDB 3.0.2, TiKV Raft log not written in time panic, panic information not written into the log file, pessimistic transaction Insert operation incorrectly performed, deadlock detector pessimistic locking, GC in the Titan storage engine, tikv-ctl Region size, PD Scatter Region scheduler cannot work, pd-ctl merge Region, pd-ctl remove-tombstone, scan Region overlapping key scope, PD members added successfully retrying mechanism, TiDB Binlog configuration item check feature, Drainer node-id configuration, TiDB Lightning tikv_gc_life_time checksums, TiDB Lightning configuration item check feature
- Follow-up Guidance: The chunk also separates the fixes by component sections: TiKV, PD, TiDB Binlog, and TiDB Lightning.
- Classification Note: This is classified as a shared release-notes chunk because the official content groups 3.0.2 fixes across TiKV, PD, and tools rather than a single primary component.

## Official Source Content

## TiKV

- Fix the bug that TiKV panics if the Raft log is not written in time [#5160](https://github.com/tikv/tikv/pull/5160)
- Fix the bug that the panic information is not written into the log file after TiKV panics [#5198](https://github.com/tikv/tikv/pull/5198)
- Fix the bug that the Insert operation might be incorrectly performed in the pessimistic transaction [#5203](https://github.com/tikv/tikv/pull/5203)
- Lower the output level of some logs that require no manual intervention to INFO [#5193](https://github.com/tikv/tikv/pull/5193)
- Improve the accuracy of monitoring the storage engine size [#5200](https://github.com/tikv/tikv/pull/5200)
- Improve the accuracy of the Region size in tikv-ctl [#5195](https://github.com/tikv/tikv/pull/5195)
- Improve the performance of the deadlock detector for pessimistic locking [#5192](https://github.com/tikv/tikv/pull/5192)
- Improve the performance of GC in the Titan storage engine [#5197](https://github.com/tikv/tikv/pull/5197)
## PD

- Fix the bug that the Scatter Region scheduler cannot work [#1642](https://github.com/pingcap/pd/pull/1642)
- Fix the bug that the merge Region operation cannot be performed in pd-ctl [#1653](https://github.com/pingcap/pd/pull/1653)
- Fix the bug that the remove-tombstone operation cannot be performed in pd-ctl [#1651](https://github.com/pingcap/pd/pull/1651)
- Fix the issue that the Region overlapping with the key scope cannot be found when performing the scan Region operation [#1648](https://github.com/pingcap/pd/pull/1648)
- Add the retrying mechanism to make sure that the members are added successfully in PD [#1643](https://github.com/pingcap/pd/pull/1643)
## Tools

TiDB Binlog

- Add the configuration item check feature when starting, which will stop the Binlog service and report an error when an invalid item is found [#687](https://github.com/pingcap/tidb-binlog/pull/687)
- Add the `node-id` configuration in Drainer to specify a specific logic used by Drainer [#684](https://github.com/pingcap/tidb-binlog/pull/684)

TiDB Lightning

- Fix the issue that `tikv_gc_life_time` fails to be changed back to its original value when 2 checksums are running at the same time [#218](https://github.com/pingcap/tidb-lightning/pull/218)
- Add the configuration item check feature when starting, which will stop the Binlog service and report an error when an invalid item is found [#217](https://github.com/pingcap/tidb-lightning/pull/217)
