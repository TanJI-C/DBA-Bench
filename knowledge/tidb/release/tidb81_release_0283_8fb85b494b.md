# TiDB 5.4.3 release overview and improvements

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.4.3.md`
- Source Title: `TiDB 5.4.3 Release Notes`
- Source Heading Path: `TiDB 5.4.3 Release Notes | TiDB 5.4.3 Release Notes > Improvements`
- Source Line Ranges: `5-28`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tikv`, `lightning`, `ticdc`
- Topic Tags: `release-notes`, `improvements`, `write-stall`, `raftstore`, `scatter-region`, `multi-region`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0283_8fb85b494b`
- Source ID: `tidb-docs-8.1:releases/release-5.4.3.md#tidb-5-4-3-release-notes`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `fe8c76161821043d9935578f4f247eeb83f30cf5d4a821955d926c86b9df8573`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.4.3#tidb-5-4-3-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.4.3.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving the TiDB 5.4.3 release overview or improvements related to TiKV write stall and Raftstore settings, TiDB Lightning Scatter Region batching, or TiCDC multi-Region runtime context switching overhead.
- Retrieval Keywords: TiDB 5.4.3 Release Notes, Improvements, TiKV, RocksDB write stall settings, flow control threshold, unreachable_backoff, Raftstore broadcasting too many messages, peer becomes unreachable, TiDB Lightning, Scatter Region, batch mode, stability of the Scatter Region process, TiCDC, multi-Region scenarios, runtime context switching, performance overhead
- Follow-up Guidance: 
- Classification Note: This chunk is classified as a release overview and improvements section because the official content lists improvement items for TiKV, TiDB Lightning, and TiCDC in TiDB 5.4.3.

## Official Source Content

# TiDB 5.4.3 Release Notes

Release date: October 13, 2022

TiDB version: 5.4.3
## Improvements

+ TiKV

    - Support configuring the RocksDB write stall settings to a value smaller than the flow control threshold [#13467](https://github.com/tikv/tikv/issues/13467)
    - Support configuring the `unreachable_backoff` item to avoid Raftstore broadcasting too many messages after one peer becomes unreachable [#13054](https://github.com/tikv/tikv/issues/13054)

+ Tools

    + TiDB Lightning

        - Optimize Scatter Region to batch mode to improve the stability of the Scatter Region process [#33618](https://github.com/pingcap/tidb/issues/33618)

    + TiCDC

        - Reduce performance overhead caused by runtime context switching in multi-Region scenarios [#5610](https://github.com/pingcap/tiflow/issues/5610)
