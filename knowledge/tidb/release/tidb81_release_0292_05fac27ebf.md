# Improvements across PD, TiFlash, BR, TiCDC, DM, and Lightning

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.0.0-dmr.md`
- Source Title: `TiDB 6.0.0 Release Notes`
- Source Heading Path: `TiDB 6.0.0 Release Notes > Improvements`
- Source Line Ranges: `622-661`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `pd`, `tiflash`, `br`, `ticdc`, `dm`, `lightning`, `tidb`, `tikv`
- Topic Tags: `release-notes`, `improvements`, `scheduling`, `leader-eviction`, `raft`, `replication`, `restore`, `placement-rules`, `grafana`, `changefeed`, `kafka`, `precheck`, `retry`, `passwords`, `error-codes`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0292_05fac27ebf`
- Source ID: `tidb-docs-8.1:releases/release-6.0.0-dmr.md#improvements`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f83aa24728ff366de561f9d0cdaa46d2007c12b5d7ece637b638384bca7b2635`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.0.0-dmr#improvements
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.0.0-dmr.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 6.0.0 improvement notes across PD, TiFlash, BR, TiCDC, DM, and TiDB Lightning such as leader eviction, `profiles.default.dt_enable_logical_split`, `--with-tidb-placement-mode`, `Lag analyze`, Kafka producer configuration, precheck, retryable errors, base64 password strings, or standardized error codes.
- Retrieval Keywords: TiDB 6.0.0 Improvements, PD leader eviction fastest object for transfer, forbid deleting a voter from a 2-replica Raft group, balance leader scheduling, TiFlash profiles.default.dt_enable_logical_split, logical splitting of TiFlash files, TiFlash replica creation for small tables, BR restore speed 2.66 GiB/s, BR --with-tidb-placement-mode, importing and exporting placement rules, TiCDC Lag analyze panel in Grafana, TiCDC support placement rules, TiCDC exponential backoff restarting a changefeed, TiCDC MySQL sink read-committed, TiCDC validate changefeed parameters upon creation, TiCDC Kafka producer configurable, DM optimistic mode inconsistent upstream table schemas, DM task in the stopped state, DM-worker working directory rather than /tmp, DM precheck improved, TiDB Lightning retryable error types, TiDB Lightning base64 format password string, TiDB Lightning standardize error codes and error outputs
- Follow-up Guidance: The chunk also lists related improvements for TiCDC HTTP API handling, DM cleanup of internal files after the task is stopped, and TiFlash cluster management integration into TiDB.
- Classification Note: This is a release-notes improvements chunk because the official content enumerates new capabilities and optimizations across multiple components in TiDB 6.0.0.

## Official Source Content

- Support automatically selecting the fastest object for transfer when evicting the leader, which helps speed up the eviction process [#4229](https://github.com/tikv/pd/issues/4229)
    - Forbid deleting a voter from a 2-replica Raft group in case the Region becomes unavailable [#4564](https://github.com/tikv/pd/issues/4564)
    - Speed up the scheduling of the balance leader [#4652](https://github.com/tikv/pd/issues/4652)

+ TiFlash

    - Forbid the logical splitting of TiFlash files (by adjusting the default value of `profiles.default.dt_enable_logical_split` to `false`. See [user document](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-configuration#tiflash-configuration-parameters) for details) and improve the space usage efficiency of the TiFlash columnar storage so that the space occupation of a table synchronized to TiFlash is similar to the space occupation of the table in TiKV
    - Optimize the cluster management and replica replication mechanism for TiFlash by integrating the previous cluster management module into TiDB, which accelerates replica creation for small tables [#29924](https://github.com/pingcap/tidb/issues/29924)

+ Tools

    + Backup & Restore (BR)

        - Improve the speed of restoring the backup data. In the simulation test when BR restores 16 TB data to a TiKV cluster with 15 nodes (each node has 16 CPU cores), the throughput reaches 2.66 GiB/s. [#27036](https://github.com/pingcap/tidb/issues/27036)

        - Support importing and exporting placement rules. Add a `--with-tidb-placement-mode` parameter to control whether to ignore the placement rules when importing data. [#32290](https://github.com/pingcap/tidb/issues/32290)

    + TiCDC

        - Add a `Lag analyze` panel in Grafana [#4891](https://github.com/pingcap/tiflow/issues/4891)
        - Support placement rules [#4846](https://github.com/pingcap/tiflow/issues/4846)
        - Synchronize HTTP API handling [#1710](https://github.com/pingcap/tiflow/issues/1710)
        - Add the exponential backoff mechanism for restarting a changefeed [#3329](https://github.com/pingcap/tiflow/issues/3329)
        - Set the default isolation level of MySQL sink to read-committed to reduce deadlocks in MySQL [#3589](https://github.com/pingcap/tiflow/issues/3589)
        - Validate changefeed parameters upon creation and refine error messages [#1716](https://github.com/pingcap/tiflow/issues/1716) [#1718](https://github.com/pingcap/tiflow/issues/1718) [#1719](https://github.com/pingcap/tiflow/issues/1719) [#4472](https://github.com/pingcap/tiflow/issues/4472)
        - Expose configuration parameters of the Kafka producer to make them configurable in TiCDC [#4385](https://github.com/pingcap/tiflow/issues/4385)

    + TiDB Data Migration (DM)

        - Support starting a task when upstream table schemas are inconsistent and in optimistic mode [#3629](https://github.com/pingcap/tiflow/issues/3629) [#3708](https://github.com/pingcap/tiflow/issues/3708) [#3786](https://github.com/pingcap/tiflow/issues/3786)
        - Support creating a task in the `stopped` state [#4484](https://github.com/pingcap/tiflow/issues/4484)
        - Support Syncer using the working directory of the DM-worker rather than `/tmp` to write internal files, and cleaning the directory after the task is stopped [#4107](https://github.com/pingcap/tiflow/issues/4107)
        - Precheck has improved. Some important checks are no longer skipped. [#3608](https://github.com/pingcap/tiflow/issues/3608)

    + TiDB Lightning

        - Add more retryable error types [#31376](https://github.com/pingcap/tidb/issues/31376)
        - Support the base64 format password string [#31194](https://github.com/pingcap/tidb/issues/31194)
        - Standardize error codes and error outputs [#32239](https://github.com/pingcap/tidb/issues/32239)
