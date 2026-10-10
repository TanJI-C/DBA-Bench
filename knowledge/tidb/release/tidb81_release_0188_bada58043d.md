# Bug fixes for PD, TiFlash, and tools

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-4.0.6.md`
- Source Title: `TiDB 4.0.6 Release Notes`
- Source Heading Path: `TiDB 4.0.6 Release Notes > Bug Fixes`
- Source Line Ranges: `160-197`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `pd`, `tiflash`, `ticdc`, `br`, `dumpling`, `lightning`
- Topic Tags: `bug-fixes`, `configuration`, `bootstrap`, `replication`, `cdc`, `backup-restore`, `export`, `import`, `grafana`, `kafka`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0188_bada58043d`
- Source ID: `tidb-docs-8.1:releases/release-4.0.6.md#bug-fixes`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `11791941b5826d46c19889aa37d39bd00abde5fec50c1e48f71308379939f834`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-4.0.6#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-4.0.6.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 4.0.6 bug fixes for PD bootstrap and scheduler behavior, TiFlash availability and correctness issues, or tool fixes for TiCDC, BR, Dumpling, and TiDB Lightning.
- Retrieval Keywords: PD initial-cluster-token, prevent different clusters from communicating with each other during bootstrap, store limit rate auto mode, scheduler persist configuration without solving errors, empty HTTP response in scheduler, TiFlash might not start after upgrading to v4.0.4/v4.0.5, renaming the primary key column, modifying the column's nullable attribute, computing a table's replication status, TiFlash not available for data reads after unsupported DDL operations, unsupported collations treated as utf8mb4_bin, QPS panel for the TiFlash coprocessor executor always displays 0 in Grafana, FROM_UNIXTIME NULL, TiCDC leaks memory, TiCDC panic in Kafka sink, CommitTs or ResolvedTs less than resolvedTs, changefeed blocked by MySQL driver, incorrect Resolved Ts interval, BR panic during checksum, BR panic after the change of PD Leader, Dumpling NULL value for the binary type, TiDB Lightning failed operations of writes and ingests displayed as successful, checkpoint updates might not be written to the database before TiDB Lightning exits
- Follow-up Guidance: 
- Classification Note: The official content is a continuation of the TiDB 4.0.6 Bug Fixes section, specifically listing fixes for PD, TiFlash, and related tools.

## Official Source Content

- Add the `initial-cluster-token` configuration to prevent different clusters from communicating with each other during bootstrap [#2922](https://github.com/pingcap/pd/pull/2922)
    - Fix the unit of store limit rate when the mode is `auto` [#2826](https://github.com/pingcap/pd/pull/2826)
    - Fix the issue that some schedulers persist configuration without solving errors [#2818](https://github.com/tikv/pd/pull/2818)
    - Fix the empty HTTP response in scheduler [#2871](https://github.com/tikv/pd/pull/2871) [#2874](https://github.com/tikv/pd/pull/2874)

+ TiFlash

    - Fix the issue that after renaming the primary key column in previous versions, TiFlash might not start after upgrading to v4.0.4/v4.0.5
    - Fix the exceptions that occur after modifying the column's `nullable` attribute
    - Fix the crash caused by computing a table's replication status
    - Fix the issue that TiFlash is not available for data reads after users applied unsupported DDL operations
    - Fix the exceptions caused by unsupported collations which are treated as `utf8mb4_bin`
    - Fix the issue that the QPS panel for the TiFlash coprocessor executor always displays `0` in Grafana
    - Fix the wrong result of the `FROM_UNIXTIME` function when input is `NULL`

+ Tools

    + TiCDC

        - Fix the issue that TiCDC leaks memory in some cases [#942](https://github.com/pingcap/tiflow/pull/942)
        - Fix the issue that TiCDC might panic in Kafka sink [#912](https://github.com/pingcap/tiflow/pull/912)
        - Fix the issue that CommitTs or ResolvedTs (CRTs) might be less than `resolvedTs` in puller [#927](https://github.com/pingcap/tiflow/pull/927)
        - Fix the issue that `changefeed` might be blocked by MySQL driver [#936](https://github.com/pingcap/tiflow/pull/936)
        - Fix the incorrect Resolved Ts interval of TiCDC [#8573](https://github.com/tikv/tikv/pull/8573)

    + Backup & Restore (BR)

        - Fix a panic that might occur during checksum [#479](https://github.com/pingcap/br/pull/479)
        - Fix a panic that might occur after the change of PD Leader [#496](https://github.com/pingcap/br/pull/496)

    + Dumpling

        - Fix the issue that the `NULL` value for the binary type is not handled properly [#137](https://github.com/pingcap/dumpling/pull/137)

    + TiDB Lightning

        - Fix the issue that all failed operations of writes and ingests are mistakenly displayed as successful [#381](https://github.com/pingcap/tidb-lightning/pull/381)
        - Fix the issue that some checkpoint updates might not be written to the database before TiDB Lightning exits [#386](https://github.com/pingcap/tidb-lightning/pull/386)
