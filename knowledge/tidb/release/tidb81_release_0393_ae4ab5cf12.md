# TiCDC bug fixes for object storage, replication stability, memory control, and upgrade behavior

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.5.2.md`
- Source Title: `TiDB 6.5.2 Release Notes`
- Source Heading Path: `TiDB 6.5.2 Release Notes > Bug fixes`
- Source Line Ranges: `97-108`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `pd`
- Topic Tags: `bug-fixes`, `object-storage`, `data-loss`, `replication`, `ddl`, `memory-usage`, `redo-log`, `kubernetes`, `kafka`, `changefeed`, `network-isolation`, `upgrade`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0393_ae4ab5cf12`
- Source ID: `tidb-docs-8.1:releases/release-6.5.2.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `54377e7627b9a07ffcc9f7507ab2d0eced76458af1e8e0a37a45cee0ff2be201`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.5.2#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.5.2.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 6.5.2 TiCDC bug fixes related to object storage replication, data loss, stuck replication, db sorter memory control, Redo log apply, Duplicate entry errors, PD network isolation, Kubernetes graceful upgrade, Kafka unavailability, or changefeed restart checkpoint issues.
- Retrieval Keywords: TiDB 6.5.2 Release Notes, TiCDC bug fixes, object storage, partition separator does not work, table scheduling might cause data loss, replication gets stuck due to non-reentrant DDL statements, TiCDC scaling might cause data loss, db sorter, cgroup memory limit, Redo log, UPDATE and INSERT disorder, Duplicate entry, network isolation between PD and TiCDC, graceful upgrade for TiCDC clusters fails on Kubernetes, all downstream Kafka servers are unavailable, restarting the changefeed might cause data loss, checkpoint cannot advance
- Follow-up Guidance: 
- Classification Note: This chunk is classified as a TiCDC release-note bug-fix entry because the official content lists resolved TiCDC issues affecting replication stability, object storage behavior, memory usage, upgrade behavior, and downstream connectivity.

## Official Source Content

- Fix the issue that the partition separator does not work when TiCDC replicates data to object storage [#8581](https://github.com/pingcap/tiflow/issues/8581) @[CharlesCheung96](https://github.com/CharlesCheung96) @[hi-rustin](https://github.com/Rustin170506)
        - Fix the issue that table scheduling might cause data loss when TiCDC replicates data to object storage [#8256](https://github.com/pingcap/tiflow/issues/8256) @[zhaoxinyu](https://github.com/zhaoxinyu)
        - Fix the issue that the replication gets stuck due to non-reentrant DDL statements [#8662](https://github.com/pingcap/tiflow/issues/8662) @[hicqu](https://github.com/hicqu)
        - Fix the issue that TiCDC scaling might cause data loss when TiCDC replicates data to object storage [#8666](https://github.com/pingcap/tiflow/issues/8666) @[CharlesCheung96](https://github.com/CharlesCheung96)
        - Fix the issue that the memory usage of `db sorter` is not controlled by `cgroup memory limit` [#8588](https://github.com/pingcap/tiflow/issues/8588) @[amyangfei](https://github.com/amyangfei)
        - Fix the issue that data loss might occur in special cases during the apply of Redo log [#8591](https://github.com/pingcap/tiflow/issues/8591) @[CharlesCheung96](https://github.com/CharlesCheung96)
        - Fix the issue that the memory usage of `db sorter` is not controlled by `cgroup memory limit` [#8588](https://github.com/pingcap/tiflow/issues/8588) @[amyangfei](https://github.com/amyangfei)
        - Fix the issue that the disorder of `UPDATE` and `INSERT` statements during data replication might cause the `Duplicate entry` error [#8597](https://github.com/pingcap/tiflow/issues/8597) @[sdojjy](https://github.com/sdojjy)
        - Fix the abnormal exit issue of the TiCDC service caused by network isolation between PD and TiCDC [#8562](https://github.com/pingcap/tiflow/issues/8562) @[overvenus](https://github.com/overvenus)
        - Fix the issue that graceful upgrade for TiCDC clusters fails on Kubernetes [#8484](https://github.com/pingcap/tiflow/issues/8484) @[overvenus](https://github.com/overvenus)
        - Fix the issue that the TiCDC server panics when all downstream Kafka servers are unavailable [#8523](https://github.com/pingcap/tiflow/issues/8523) @[3AceShowHand](https://github.com/3AceShowHand)
        - Fix the issue that restarting the changefeed might cause data loss or that the checkpoint cannot advance [#8242](https://github.com/pingcap/tiflow/issues/8242) @[overvenus](https://github.com/overvenus)
