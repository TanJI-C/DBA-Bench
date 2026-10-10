# Bug fixes for TiCDC and TiDB Lightning

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.3.0.md`
- Source Title: `TiDB 7.3.0 Release Notes`
- Source Heading Path: `TiDB 7.3.0 Release Notes > Bug fixes`
- Source Line Ranges: `316-326`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `ticdc`, `pd`, `lightning`, `tidb`
- Topic Tags: `bug-fixes`, `changefeed`, `pd-availability`, `network-isolation`, `kafka-sink`, `panic`, `enum-encoding`, `checksum`, `ssl`, `logical-import`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0501_0bddf2e243`
- Source ID: `tidb-docs-8.1:releases/release-7.3.0.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `230ea407c25d02892fe7e95d8cf0b0cb2545646ab97b7120f0e7ffb2e3c11c4e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.3.0#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.3.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 7.3.0 bug fixes related to TiCDC changefeed behavior or TiDB Lightning import and checksum issues.
- Retrieval Keywords: TiDB 7.3.0 bug fixes, TiCDC changefeed fail temporary unavailability of PD, #9294, TiCDC network isolation data inconsistency, #9344, Kafka Sink errors indefinitely block changefeed progress, #9309, TiCDC panic when node status changes, #9354, default ENUM values encoding error, #9259, TiDB Lightning checksum SSL errors after import, #45462, Logical Import Mode deleting tables downstream metadata not updated in time, #44614
- Follow-up Guidance: The chunk also lists specific issue identifiers for each TiCDC and TiDB Lightning bug fix in TiDB 7.3.0.
- Classification Note: This is a release-note bug-fix entry because the official content enumerates resolved issues for TiCDC and TiDB Lightning in TiDB 7.3.0.

## Official Source Content

- Fix the issue that changefeeds would fail due to the temporary unavailability of PD [#9294](https://github.com/pingcap/tiflow/issues/9294) @[asddongmen](https://github.com/asddongmen)
        - Fix the data inconsistency issue that might occur when some TiCDC nodes are isolated from the network [#9344](https://github.com/pingcap/tiflow/issues/9344) @[CharlesCheung96](https://github.com/CharlesCheung96)
        - Fix the issue that when Kafka Sink encounters errors it might indefinitely block changefeed progress [#9309](https://github.com/pingcap/tiflow/issues/9309) @[hicqu](https://github.com/hicqu)
        - Fix the panic issue that might occur when the TiCDC node status changes [#9354](https://github.com/pingcap/tiflow/issues/9354) @[sdojjy](https://github.com/sdojjy)
        - Fix the encoding error for the default `ENUM` values [#9259](https://github.com/pingcap/tiflow/issues/9259) @[3AceShowHand](https://github.com/3AceShowHand)

    + TiDB Lightning

        - Fix the issue that executing checksum after TiDB Lightning completes import might get SSL errors [#45462](https://github.com/pingcap/tidb/issues/45462) @[D3Hunter](https://github.com/D3Hunter)
        - Fix the issue that in Logical Import Mode, deleting tables downstream during import might cause TiDB Lightning metadata not to be updated in time [#44614](https://github.com/pingcap/tidb/issues/44614) @[dsdashun](https://github.com/dsdashun)
