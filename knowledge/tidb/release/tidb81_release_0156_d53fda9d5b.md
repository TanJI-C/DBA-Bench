# Bug fixes for TiKV, PD, TiFlash, TiCDC, Binlog, and BR

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-4.0.0-rc.2.md`
- Source Title: `TiDB 4.0 RC.2 Release Notes`
- Source Heading Path: `TiDB 4.0 RC.2 Release Notes > Bug Fixes`
- Source Line Ranges: `153-197`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tikv`, `pd`, `tiflash`, `ticdc`, `br`, `ecosystem`, `dashboard`
- Topic Tags: `bug-fixes`, `restore`, `raftstore`, `diagnostics`, `memory`, `encryption`, `grafana`, `binlog`, `replication`, `backup`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0156_d53fda9d5b`
- Source ID: `tidb-docs-8.1:releases/release-4.0.0-rc.2.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9f5331ad59925103028e7870b60a405dd12ba0b66635a15af160e0cae97c4a72`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-4.0.0-rc.2#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-4.0.0-rc.2.md

## Retrieval Guidance

- Use When: Use this chunk when looking for RC.2 bug fixes across TiKV, PD, TiFlash, TiCDC, Binlog, or BR, especially restore, Raftstore, diagnostics, encryption, and Grafana-related issues.
- Retrieval Keywords: TiKV, PD, TiFlash, TiCDC, TiDB Binlog, Backup & Restore (BR), restoration, Raftstore, pd-ctl, Grafana dashboard, snapshot ingestion, encryption at rest
- Follow-up Guidance: Review the component subsections for the exact problem descriptions and fixes.
- Classification Note: This combined section lists RC.2 bug fixes for TiKV, PD, TiFlash, TiCDC, Binlog, and BR.

## Official Source Content

- Fix the issue that many empty Regions are generated after restoration [#7632](https://github.com/tikv/tikv/pull/7632)
    - Fix the panic issue of Raftstore when receiving out-of-order read index responses [#7370](https://github.com/tikv/tikv/pull/7370)
    - Fix the issue that an invalid storage or coprocessor read pool configuration might not be rejected when the unified thread pool is enabled [#7513](https://github.com/tikv/tikv/pull/7513)
    - Fix the panic issue of the `join` operation when the TiKV server is shut down [#7713](https://github.com/tikv/tikv/pull/7713)
    - Fix the issue that no result is returned when searching TiKV slow logs via diagnostics API [#7776](https://github.com/tikv/tikv/pull/7776)
    - Fix the issue that notable memory fragmentation is generated when the TiKV node is running for a long time [#7556](https://github.com/tikv/tikv/pull/7556)
    - Fix the issue that the SQL statement fails to execute when an invalid date is stored [#7268](https://github.com/tikv/tikv/pull/7268)
    - Fix the issue that the backup data cannot be restored from GCS [#7739](https://github.com/tikv/tikv/pull/7739)
    - Fix the issue that KMS key ID is not validated during encryption at rest [#7719](https://github.com/tikv/tikv/pull/7719)
    - Fix the underlying correctness issue of the Coprocessor in compilers of different architecture  [#7714](https://github.com/tikv/tikv/pull/7714) [#7730](https://github.com/tikv/tikv/pull/7730)
    - Fix the `snapshot ingestion` error when encryption is enabled [#7815](https://github.com/tikv/tikv/pull/7815)
    - Fix the `Invalid cross-device link` error when rewriting the configuration file [#7817](https://github.com/tikv/tikv/pull/7817)
    - Fix the issue of wrong toml format when writing the configuration file to an empty file [#7817](https://github.com/tikv/tikv/pull/7817)
    - Fix the issue that a destroyed peer in Raftstore can still process requests [#7836](https://github.com/tikv/tikv/pull/7836)

+ PD

    - Fix the `404` issue that occurs when using the `region key` command in pd-ctl [#2399](https://github.com/pingcap/pd/pull/2399)
    - Fix the issue that the monitor metrics of TSO and ID allocation are missing from the Grafana dashboard [#2405](https://github.com/pingcap/pd/pull/2405)
    - Fix the issue that pd-recover is not included in the Docker image [#2406](https://github.com/pingcap/pd/pull/2406)
    - Parse the path of data directory to an absolute path to fix the issue that TiDB Dashboard might not correctly display PD information [#2420](https://github.com/pingcap/pd/pull/2420)
    - Fix the issue that there is no default output when using the `scheduler config shuffle-region-scheduler` command in pd-ctl [#2416](https://github.com/pingcap/pd/pull/2416)

+ TiFlash

    - Fix the issue that the wrong information of used capacity is report in some scenarios

+ Tools

    - TiDB Binlog

        - Fix the issue that data of the `mediumint` type is not processed when the downstream is Kafka [#962](https://github.com/pingcap/tidb-binlog/pull/962)
        - Fix the issue that the reparo fails to parse the DDL statement when the database name in DDL is a keyword [#961](https://github.com/pingcap/tidb-binlog/pull/961)

    - TiCDC

        - Fix the issue of using the wrong time zone when the `TZ` environment variable is not set [#512](https://github.com/pingcap/tiflow/pull/512)
        - Fix the issue that the owner does not clean up the resources when the server exits because some errors are not handled correctly [#528](https://github.com/pingcap/tiflow/pull/528)
        - Fix the issue that TiCDC might be stuck when reconnecting to TiKV [#531](https://github.com/pingcap/tiflow/pull/531)
        - Optimize the memory usage when initializing the table schema [#534](https://github.com/pingcap/tiflow/pull/534)
        - Use the `watch` mode to monitor the replication status changes and perform quasi-real-time updates to reduce replication delay [#481](https://github.com/pingcap/tiflow/pull/481)

    + Backup & Restore (BR)

        - Fix the issue that inserting data might trigger the `duplicate entry` error after BR restores a table with the `auto_random` attribute [#241](https://github.com/pingcap/br/issues/241)
