# Bug fixes for TiCDC, DM, and TiDB Lightning

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.5.2.md`
- Source Title: `TiDB 7.5.2 Release Notes`
- Source Heading Path: `TiDB 7.5.2 Release Notes > Bug fixes`
- Source Line Ranges: `228-253`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `dm`, `lightning`, `pd`
- Topic Tags: `bug-fixes`, `replication`, `changefeed`, `ddl-replication`, `data-consistency`, `owner-eviction`, `timezone`, `csv-sink`, `connection-blocking`, `data-import`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0537_8e45176d6c`
- Source ID: `tidb-docs-8.1:releases/release-7.5.2.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `37a906abb550eff3848f77d93d80e68c32490d891d708c0802bd913f4e231103`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.5.2#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.5.2.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 7.5.2 bug fixes for TiCDC replication or changefeed issues, DM data migration problems, or TiDB Lightning import failures and panics.
- Retrieval Keywords: TiDB 7.5.2 release notes bug fixes, TiCDC high latency in PD disk I/O severe latency in data replication, /api/v2/owner/resign, evicts the TiCDC owner node, wrong CSV file due to wrong BarrierTS, TIMESTAMP type checksum time zone mismatch, data integrity validation for single-row data, changefeed eventual consistency enabled object storage sink temporary failure, DROP PRIMARY KEY not replicated correctly, DROP UNIQUE KEY not replicated correctly, TiCDC panics when scheduling table replication tasks, downstream Pulsar is stopped removing the changefeed causes process to get stuck, restarting PD might cause the TiCDC node to restart with an error, open-protocol old value part incorrectly outputs the default value, TIMEZONE type default value incorrect time zone, Exchange Partition ... With Validation, data race in the KV client causes TiCDC to panic, updating the primary key or the unique key in upstream might cause data inconsistency, DM connection blocking issue, go-mysql, data is lost when the upstream primary key is of binary type, TiDB Lightning might fail to import data when EBS BR is running, no database selected during data import, invalid store ID 0, killing the PD Leader, empty table of Parquet format
- Follow-up Guidance: This chunk also includes DM fixes for connection blocking and binary primary key data loss, plus TiDB Lightning fixes for EBS BR interference, `no database selected`, `invalid store ID 0`, and Parquet empty-table panic.
- Classification Note: The classification is release/ticdc because the official content is a TiDB 7.5.2 Bug fixes section centered on TiCDC and followed by related DM and TiDB Lightning fixes.

## Official Source Content

- Fix the issue that high latency in the PD disk I/O causes severe latency in data replication [#9054](https://github.com/pingcap/tiflow/issues/9054) @[asddongmen](https://github.com/asddongmen)
        - Fix the issue that calling the API (`/api/v2/owner/resign`) that evicts the TiCDC owner node causes the TiCDC task to restart unexpectedly [#10781](https://github.com/pingcap/tiflow/issues/10781) @[sdojjy](https://github.com/sdojjy)
        - Fix the issue that data is written to a wrong CSV file due to wrong BarrierTS in scenarios where DDL statements are executed frequently [#10668](https://github.com/pingcap/tiflow/issues/10668) @[lidezhu](https://github.com/lidezhu)
        - Fix the issue that TiCDC fails to validate `TIMESTAMP` type checksum due to time zone mismatch after data integrity validation for single-row data is enabled [#10573](https://github.com/pingcap/tiflow/issues/10573) @[3AceShowHand](https://github.com/3AceShowHand)
        - Fix the issue that a changefeed with eventual consistency enabled might fail when the object storage sink encounters a temporary failure [#10710](https://github.com/pingcap/tiflow/issues/10710) @[CharlesCheung96](https://github.com/CharlesCheung96)
        - Fix the issue that `DROP PRIMARY KEY` and `DROP UNIQUE KEY` statements are not replicated correctly [#10890](https://github.com/pingcap/tiflow/issues/10890) @[asddongmen](https://github.com/asddongmen)
        - Fix the issue TiCDC panics when scheduling table replication tasks [#10613](https://github.com/pingcap/tiflow/issues/10613) @[CharlesCheung96](https://github.com/CharlesCheung96)
        - Fix the issue that when the downstream Pulsar is stopped, removing the changefeed causes the normal TiCDC process to get stuck, which causes other changefeed processes to get stuck [#10629](https://github.com/pingcap/tiflow/issues/10629) @[asddongmen](https://github.com/asddongmen)
        - Fix the issue that restarting PD might cause the TiCDC node to restart with an error [#10799](https://github.com/pingcap/tiflow/issues/10799) @[3AceShowHand](https://github.com/3AceShowHand)
        - Fix the issue that the old value part of `open-protocol` incorrectly outputs the default value according to the `STRING` type instead of its actual type [#10803](https://github.com/pingcap/tiflow/issues/10803) @[3AceShowHand](https://github.com/3AceShowHand)
        - Fix the issue that the default value of `TIMEZONE` type is not set according to the correct time zone [#10931](https://github.com/pingcap/tiflow/issues/10931) @[3AceShowHand](https://github.com/3AceShowHand)
        - Fix the issue that TiCDC fails to execute the `Exchange Partition ... With Validation` DDL downstream after it is written upstream, causing the changefeed to get stuck [#10859](https://github.com/pingcap/tiflow/issues/10859) @[hongyunyan](https://github.com/hongyunyan)
        - Fix the issue that data race in the KV client causes TiCDC to panic [#10718](https://github.com/pingcap/tiflow/issues/10718) @[asddongmen](https://github.com/asddongmen)
        - Fix the issue that updating the primary key or the unique key in upstream might cause data inconsistency between upstream and downstream [#10918](https://github.com/pingcap/tiflow/issues/10918) @[lidezhu](https://github.com/lidezhu)

    + TiDB Data Migration (DM)

        - Fix the connection blocking issue by upgrading `go-mysql` [#11041](https://github.com/pingcap/tiflow/issues/11041) @[D3Hunter](https://github.com/D3Hunter)
        - Fix the issue that data is lost when the upstream primary key is of binary type [#10672](https://github.com/pingcap/tiflow/issues/10672) @[GMHDBJD](https://github.com/GMHDBJD)

    + TiDB Lightning

        - Fix the issue that TiDB Lightning might fail to import data when EBS BR is running [#49517](https://github.com/pingcap/tidb/issues/49517) @[mittalrishabh](https://github.com/mittalrishabh)
        - Fix the issue that TiDB Lightning reports `no database selected` during data import due to incompatible SQL statements in the source files [#51800](https://github.com/pingcap/tidb/issues/51800) @[lance6716](https://github.com/lance6716)
        - Fix the issue that killing the PD Leader causes TiDB Lightning to report the `invalid store ID 0` error during data import [#50501](https://github.com/pingcap/tidb/issues/50501) @[Leavrth](https://github.com/Leavrth)
        - Fix the issue that TiDB Lightning panics when importing an empty table of Parquet format [#52518](https://github.com/pingcap/tidb/issues/52518) @[kennytm](https://github.com/kennytm)
