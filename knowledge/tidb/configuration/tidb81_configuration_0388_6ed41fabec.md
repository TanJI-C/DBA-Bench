# TiKV load-based split thresholds and memory section start

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tikv-configuration-file.md`
- Source Title: `TiKV Configuration File`
- Source Heading Path: `TiKV Configuration File > split | TiKV Configuration File > split > `byte-threshold` <span class="version-mark">New in v5.0</span> | TiKV Configuration File > split > `qps-threshold` | TiKV Configuration File > split > `region-cpu-overload-threshold-ratio` <span class="version-mark">New in v6.2.0</span> | TiKV Configuration File > memory <span class="version-mark">New in v7.5.0</span>`
- Source Line Ranges: `2580-2609`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: none
- Topic Tags: `load-based-split`, `hotspot`, `region`, `byte-threshold`, `qps-threshold`, `cpu-threshold`, `memory`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0388_6ed41fabec`
- Source ID: `tidb-docs-8.1:tikv-configuration-file.md#split`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `657f50ad31ceb6dbbfb400f7a704543fc81f958fd79581f80aaf03680ec392f9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tikv-configuration-file#split
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tikv-configuration-file.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiKV load-based split hotspot thresholds by byte rate, QPS, or Region CPU usage, or when locating the start of the memory section.
- Retrieval Keywords: split, Load Base Split, byte-threshold, qps-threshold, region-cpu-overload-threshold-ratio, hotspot, Region is identified as a hotspot, region-split-size, 30MiB per second, 100MiB per second, 3000, 7000, 0.25, 0.75, memory
- Follow-up Guidance: The content gives threshold defaults that vary depending on whether region-split-size is less than 4 GiB or greater than or equal to 4 GiB.
- Classification Note: This is classified as configuration because the content defines TiKV split-related threshold parameters and their default values.

## Official Source Content

## split

Configuration items related to [Load Base Split](https://docs.pingcap.com/tidb/stable/configure-load-base-split).
### `byte-threshold` New in v5.0

+ Controls the traffic threshold at which a Region is identified as a hotspot.
+ Default value:

    + `30MiB` per second when [`region-split-size`](#region-split-size) is less than 4 GiB.
    + `100MiB` per second when [`region-split-size`](#region-split-size) is greater than or equal to 4 GiB.
### `qps-threshold`

+ Controls the QPS threshold at which a Region is identified as a hotspot.
+ Default value:

    + `3000` when [`region-split-size`](#region-split-size) is less than 4 GiB.
    + `7000` when  [`region-split-size`](#region-split-size) is greater than or equal to 4 GiB.
### `region-cpu-overload-threshold-ratio` New in v6.2.0

+ Controls the CPU usage threshold at which a Region is identified as a hotspot.
+ Default value:

    + `0.25` when [`region-split-size`](#region-split-size) is less than 4 GiB.
    + `0.75` when  [`region-split-size`](#region-split-size) is greater than or equal to 4 GiB.
## memory New in v7.5.0
