# TiDB 4.0.9 improvements across TiDB, TiKV, PD, TiFlash, Dashboard, and tools

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-4.0.9.md`
- Source Title: `TiDB 4.0.9 Release Notes`
- Source Heading Path: `TiDB 4.0.9 Release Notes > Improvements`
- Source Line Ranges: `38-121`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `dashboard`, `tiflash`, `br`, `ticdc`, `dumpling`, `lightning`
- Topic Tags: `release-notes`, `improvements`, `configuration`, `performance`, `monitoring`, `observability`, `backup-restore`, `replication`, `import-export`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0194_9e0e359fbb`
- Source ID: `tidb-docs-8.1:releases/release-4.0.9.md#improvements`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8fe8b0516270ff470f9d8632113bb3771f0d1cae6525e4c12c3f4356616c5ce0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-4.0.9#improvements
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-4.0.9.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 4.0.9 improvement items across core components and tools, including configuration changes, monitoring metrics, error handling, performance tuning, and tool behavior updates.
- Retrieval Keywords: TiDB 4.0.9 Release Notes Improvements, GOGC variable in the configuration file, LOCK IN SHARE MODE error message, LOAD DATA prepare error, EXPLAIN ANALYZE DML executor-related runtime information, connection idle time monitoring metric, runtime/trace slow log, pessimistic-txn.pipelined dynamically changing, ingesting SST errors monitoring metrics, apply-max-batch-size 1024, store-max-batch-size 1024, max-background-flushes, force-consistency-checks disabled by default, Tombstone cluster version check, TiDB Dashboard detailed error messages, TiFlash replica reads latency, BR --checksum=false, read index not ready, proposal in merging mode, TiCDC unified sorter experimental, Kafka sink maximum message size, Dumpling --transactional-consistency, Dumpling -c --compress, TiDB Lightning human-readable format, tikv-importer.region-split-size, TiDB Binlog Drainer non-zero code
- Follow-up Guidance: If the retrieval need is specifically about 4.0.9 compatibility changes or new features rather than improvements, consult the corresponding sections in the same release notes.
- Classification Note: This is classified as a release chunk because the official content is the Improvements section of the TiDB 4.0.9 release notes covering TiDB, TiKV, PD, TiDB Dashboard, TiFlash, and related tools.

## Official Source Content

## Improvements

+ TiDB

    - Avoid the (index) merge join in a heuristical way when converting equal conditions to other conditions [#21146](https://github.com/pingcap/tidb/pull/21146)
    - Differentiate the types of user variables [#21107](https://github.com/pingcap/tidb/pull/21107)
    - Support setting the `GOGC` variable in the configuration file [#20922](https://github.com/pingcap/tidb/pull/20922)
    - Make the dumped binary time (`Timestamp` and `Datetime`) more compatible with MySQL [#21135](https://github.com/pingcap/tidb/pull/21135)
    - Provide an error message for statements that use the `LOCK IN SHARE MODE` syntax [#21005](https://github.com/pingcap/tidb/pull/21005)
    - Avoid outputting unnecessary warnings or errors when folding constants in shortcut-able expressions [#21040](https://github.com/pingcap/tidb/pull/21040)
    - Raise an error when preparing the `LOAD DATA` statement [#21199](https://github.com/pingcap/tidb/pull/21199)
    - Ignore the attribute of the integer zero-fill size when changing the integer column types [#20986](https://github.com/pingcap/tidb/pull/20986)
    - Add the executor-related runtime information of DML statements in the result of `EXPLAIN ANALYZE` [#21066](https://github.com/pingcap/tidb/pull/21066)
    - Disallow multiple updates on the primary key in a singe SQL statements [#21113](https://github.com/pingcap/tidb/pull/21113)
    - Add a monitoring metric for the connection idle time [#21301](https://github.com/pingcap/tidb/pull/21301)
    - Temporarily enable the slow log when the `runtime/trace` tool is running [#20578](https://github.com/pingcap/tidb/pull/20578)

+ TiKV

    - Add the tag to trace the source of the `split` command [#8936](https://github.com/tikv/tikv/pull/8936)
    - Support dynamically changing the `pessimistic-txn.pipelined` configuration [#9100](https://github.com/tikv/tikv/pull/9100)
    - Reduce the impact on performance when running Backup & Restore and TiDB Lightning [#9098](https://github.com/tikv/tikv/pull/9098)
    - Add monitoring metrics for the ingesting SST errors [#9096](https://github.com/tikv/tikv/pull/9096)
    - Prevent the leader from being hibernated when some peers still need to replicate logs [#9093](https://github.com/tikv/tikv/pull/9093)
    - Increase the success rate of the pipelined pessimistic locking [#9086](https://github.com/tikv/tikv/pull/9086)
    - Change the default value of `apply-max-batch-size` and `store-max-batch-size` to `1024` [#9020](https://github.com/tikv/tikv/pull/9020)
    - Add the `max-background-flushes` configuration item [#8947](https://github.com/tikv/tikv/pull/8947)
    - Disable `force-consistency-checks` by default to improve performance [#9029](https://github.com/tikv/tikv/pull/9029)
    - Offload the queries on the Region size from `pd heartbeat worker` to `split check worker` [#9185](https://github.com/tikv/tikv/pull/9185)

+ PD

    - Check the TiKV cluster version when a TiKV stores become `Tombstone`, which prevents users from enabling incompatible features during the process of downgrade or upgrade [#3213](https://github.com/pingcap/pd/pull/3213)
    - Disallow the TiKV store of a lower version to change from `Tombstone` back to `Up` [#3206](https://github.com/pingcap/pd/pull/3206)

+ TiDB Dashboard

    - Keep expanding when "Expand" is clicked for SQL statements [#775](https://github.com/pingcap/tidb-dashboard/pull/775)
    - Open detail pages in new windows for **SQL Statements** and **Slow Queries** [#816](https://github.com/pingcap/tidb-dashboard/pull/816)
    - Improve descriptions for time-related fields in **Slow Queries** details [#817](https://github.com/pingcap/tidb-dashboard/pull/817)
    - Display detailed error messages [#794](https://github.com/pingcap/tidb-dashboard/pull/794)

+ TiFlash

    - Reduce the latency of replica reads
    - Refine TiFlash's error messages
    - Limit the memory usage of cache data when the data volume is huge
    - Add a monitoring metric for the number of coprocessor tasks being handled

+ Tools

    + Backup & Restore (BR)

        - Disallow the ambiguous `--checksum false` argument in the command line, which does not correctly disable checksum. Only `--checksum=false` is accepted. [#588](https://github.com/pingcap/br/pull/588)
        - Support changing the PD configuration temporarily so that PD can recover the original configuration after BR accidentally exists [#596](https://github.com/pingcap/br/pull/596)
        - Support analyzing tables after restore [#622](https://github.com/pingcap/br/pull/622)
        - Retry for the `read index not ready` and `proposal in merging mode` errors [#626](https://github.com/pingcap/br/pull/626)

    + TiCDC

        - Add an alert for enabling TiKV's Hibernate Region feature [#1120](https://github.com/pingcap/tiflow/pull/1120)
        - Reduce memory usage in the schema storage [#1127](https://github.com/pingcap/tiflow/pull/1127)
        - Add the feature of unified sorter, which accelerates replication when the data size of the incremental scan is large (experimental) [#1122](https://github.com/pingcap/tiflow/pull/1122)
        - Support configuring the maximum message size and the maximum message batch in the TiCDC Open Protocol message (only for Kafka sink) [#1079](https://github.com/pingcap/tiflow/pull/1079)

    + Dumpling

        - Retry dumping data on failed chunks [#182](https://github.com/pingcap/dumpling/pull/182)
        - Support configuring both the `-F` and `-r` arguments at the same time [#177](https://github.com/pingcap/dumpling/pull/177)
        - Exclude system databases in `--filter` by default [#194](https://github.com/pingcap/dumpling/pull/194)
        - Support the `--transactional-consistency` parameter and support rebuilding MySQL connections during retry [#199](https://github.com/pingcap/dumpling/pull/199)
        - Support using the `-c,--compress` parameter to specify the compression algorithm used by Dumpling. An empty string means no compression. [#202](https://github.com/pingcap/dumpling/pull/202)

    + TiDB Lightning

        - Filter out all system schemas by default [#459](https://github.com/pingcap/tidb-lightning/pull/459)
        - Support setting a default value for the auto-random primary key for the Local-backend or Importer-backend [#457](https://github.com/pingcap/tidb-lightning/pull/457)
        - Use range properties to make the range split more precise in Local-backend [#422](https://github.com/pingcap/tidb-lightning/pull/422)
        - Support a human-readable format (such as "2.5 GiB") in `tikv-importer.region-split-size`, `mydumper.read-block-size`, `mydumper.batch-size`, and `mydumper.max-region-size` [#471](https://github.com/pingcap/tidb-lightning/pull/471)

    + TiDB Binlog

        - Exit the Drainer process with the non-zero code if the upstream PD is down or if applying DDL or DML statements to the downstream fails [#1012](https://github.com/pingcap/tidb-binlog/pull/1012)
