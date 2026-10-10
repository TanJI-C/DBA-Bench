# TiKV memory heap profiling settings

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tikv-configuration-file.md`
- Source Title: `TiKV Configuration File`
- Source Heading Path: `TiKV Configuration File > memory <span class="version-mark">New in v7.5.0</span> > `enable-heap-profiling` <span class="version-mark">New in v7.5.0</span> | TiKV Configuration File > memory <span class="version-mark">New in v7.5.0</span> > `profiling-sample-per-bytes` <span class="version-mark">New in v7.5.0</span> | TiKV Configuration File > memory <span class="version-mark">New in v7.5.0</span> > `enable-thread-exclusive-arena` <span class="version-mark">New in v8.1.0</span>`
- Source Line Ranges: `2610-2623`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: none
- Topic Tags: `memory`, `heap-profiling`, `sampling`, `thread-level-memory`, `defaults`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0389_ea54ac8088`
- Source ID: `tidb-docs-8.1:tikv-configuration-file.md#enable-heap-profiling-span-class-version-mark-new-in-v7-5-0-span`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d0873350cc5ec9f8a9d354b86ca25d59e8ee86d30a7454a0c5a072d0bb16202a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tikv-configuration-file#enable-heap-profiling-span-class-version-mark-new-in-v7-5-0-span
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tikv-configuration-file.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiKV memory heap profiling settings, sampling size, or thread-level memory allocation display in the TiKV configuration file.
- Retrieval Keywords: enable-heap-profiling, profiling-sample-per-bytes, enable-thread-exclusive-arena, Heap Profiling, track the memory usage of TiKV, memory allocation status at the TiKV thread level, track the memory usage of each TiKV thread, 512KiB, default value true
- Follow-up Guidance: The content states the default values: `enable-heap-profiling` is `true`, `profiling-sample-per-bytes` is `512KiB`, and `enable-thread-exclusive-arena` is `true`.
- Classification Note: This is classified as TiKV configuration content because the source defines TiKV configuration options under the `memory` section and gives their purposes and default values.

## Official Source Content

### `enable-heap-profiling` New in v7.5.0

+ Controls whether to enable Heap Profiling to track the memory usage of TiKV.
+ Default value: `true`
### `profiling-sample-per-bytes` New in v7.5.0

+ Specifies the amount of data sampled by Heap Profiling each time, rounding up to the nearest power of 2.
+ Default value: `512KiB`
### `enable-thread-exclusive-arena` New in v8.1.0

+ Controls whether to display the memory allocation status at the TiKV thread level to track the memory usage of each TiKV thread.
+ Default value: `true`
