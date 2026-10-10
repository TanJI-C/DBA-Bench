# TiDB 4.0.12 improvements across TiDB TiKV PD TiFlash and tools

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-4.0.12.md`
- Source Title: `TiDB 4.0.12 Release Notes`
- Source Heading Path: `TiDB 4.0.12 Release Notes > Improvements`
- Source Line Ranges: `18-75`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `tiflash`, `ticdc`, `br`, `lightning`
- Topic Tags: `release-notes`, `improvements`, `explain`, `slow-log`, `ddl`, `partitioning`, `leader-transfer`, `region-cache`, `backup-performance`, `import-performance`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0164_6651f1ae1d`
- Source ID: `tidb-docs-8.1:releases/release-4.0.12.md#improvements`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b7edcddbc659aaf02ddf1043971240ea8ec5049d4c433ed3d99edaa275266381`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-4.0.12#improvements
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-4.0.12.md

## Retrieval Guidance

- Use When: Use this chunk when searching TiDB 4.0.12 improvements across TiDB, TiKV, PD, TiFlash, TiCDC, BR, or TiDB Lightning, especially for `EXPLAIN`, slow log fields, `infoschema.partitions`, Region cache, backup performance, or import memory settings.
- Retrieval Keywords: TiDB 4.0.12 improvements, EXPLAIN batch cop output, warning information for expressions that cannot be pushed to the storage layer, optimization-time, wait-TS-time, slow log, partition_id, infoschema.partitions, last_plan_from_binding, PREPARE execution failure, Failed Query OPM, tidb_snapshot, leader-transfer-max-log-lag, 128, Region cache, pending-peers, down-peers, split-cache, TiFlash configuration file remove useless items, adaptive aggressive GC, TiCDC start-ts checkpoint-ts, Grafana panels for the Old Value feature, HTTP_PROXY, HTTPS_PROXY, service safe point check, cluster_version, br_version, backupmeta, tikv-importer.engine-mem-cache-size, tikv-importer.local-writer-mem-cache-size, batch split region, Local-backend, s3:ListBucket, resuming from a checkpoint
- Follow-up Guidance: 
- Classification Note: This is an improvements release-note chunk because it lists enhancement items for TiDB, TiKV, PD, TiFlash, TiCDC, BR, and TiDB Lightning in 4.0.12.

## Official Source Content

## Improvements

+ TiDB

    - Refine the output information of the `EXPLAIN` statement for the `batch cop` mode [#23164](https://github.com/pingcap/tidb/pull/23164)
    - Add the warning information for expressions that cannot be pushed to the storage layer in the output of the `EXPLAIN` statement [#23020](https://github.com/pingcap/tidb/pull/23020)
    - Migrate a part of the DDL package code from `Execute`/`ExecRestricted` to the safe API (2) [#22935](https://github.com/pingcap/tidb/pull/22935)
    - Migrate a part of the DDL package code from `Execute`/`ExecRestricted` to the safe API (1) [#22929](https://github.com/pingcap/tidb/pull/22929)
    - Add `optimization-time` and `wait-TS-time` into the slow log [#22918](https://github.com/pingcap/tidb/pull/22918)
    - Support querying `partition_id` from the `infoschema.partitions` table [#22489](https://github.com/pingcap/tidb/pull/22489)
    - Add `last_plan_from_binding` to help the users know whether a SQL statement's execution plan is matched with the hints in the binding [#21430](https://github.com/pingcap/tidb/pull/21430)
    - Scatter truncated tables without the `pre-split` option [#22872](https://github.com/pingcap/tidb/pull/22872)
    - Add three format specifiers for the `str_to_date` expression [#22812](https://github.com/pingcap/tidb/pull/22812)
    - Record the `PREPARE` execution failure as `Failed Query OPM` in the metrics monitor [#22672](https://github.com/pingcap/tidb/pull/22672)
    - Do not report errors for the `PREPARE` execution if `tidb_snapshot` is set [#22641](https://github.com/pingcap/tidb/pull/22641)

+ TiKV

    - Prevent a large number of reconnections in a short period of time [#9879](https://github.com/tikv/tikv/pull/9879)
    - Optimize the write operations and Batch Get in the scenarios of many tombstones [#9729](https://github.com/tikv/tikv/pull/9729)
    - Change the default value of `leader-transfer-max-log-lag` to `128` to increase the success rate of leader transfer [#9605](https://github.com/tikv/tikv/pull/9605)

+ PD

    - Update the Region cache only when `pending-peers` or `down-peers` changes, which reduces the pressure of updating heartbeats [#3471](https://github.com/pingcap/pd/pull/3471)
    - Prevent the Regions in `split-cache` from becoming the target of merge [#3459](https://github.com/pingcap/pd/pull/3459)

+ TiFlash

    - Optimize the configuration file and remove useless items
    - Reduce the size of TiFlash binary files
    - Use an adaptive aggressive GC strategy to reduce memory usage

+ Tools

    + TiCDC

        - Add a double confirmation when users create or resume the changefeed with the `start-ts` or `checkpoint-ts` 1 day before the current timestamp [#1497](https://github.com/pingcap/tiflow/pull/1497)
        - Add Grafana panels for the Old Value feature [#1571](https://github.com/pingcap/tiflow/pull/1571)

    + Backup & Restore (BR)

        - Log the `HTTP_PROXY` and `HTTPS_PROXY` environmental variables [#827](https://github.com/pingcap/br/pull/827)
        - Improve the backup performance when there are many tables [#745](https://github.com/pingcap/br/pull/745)
        - Report errors if the service safe point check fails [#826](https://github.com/pingcap/br/pull/826)
        - Add the `cluster_version` and `br_version` information in `backupmeta` [#803](https://github.com/pingcap/br/pull/803)
        - Add retry for external storage errors to increase the success rate of backup [#851](https://github.com/pingcap/br/pull/851)
        - Reduce memory usage during backup [#886](https://github.com/pingcap/br/pull/886)

    + TiDB Lightning

        - Check the TiDB cluster version before running TiDB Lightning to avoid unexpected errors [#787](https://github.com/pingcap/br/pull/787)
        - Fail fast when TiDB Lightning meets the `cancel` error [#867](https://github.com/pingcap/br/pull/867)
        - Add `tikv-importer.engine-mem-cache-size` and `tikv-importer.local-writer-mem-cache-size` configuration items to balance between memory usage and performance [#866](https://github.com/pingcap/br/pull/866)
        - Run `batch split region` in parallel for TiDB Lightning's Local-backend to increase the import speed [#868](https://github.com/pingcap/br/pull/868)
        - When using TiDB Lightning to import data from a S3 storage, TiDB Lightning no longer requires the `s3:ListBucket` permission [#919](https://github.com/pingcap/br/pull/919)
        - When resuming from a checkpoint, TiDB Lightning keeps using the original engine [#924](https://github.com/pingcap/br/pull/924)
