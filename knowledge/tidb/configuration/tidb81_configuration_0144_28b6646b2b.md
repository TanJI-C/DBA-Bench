# Configure Runtime Filter mode

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/runtime-filter.md`
- Source Title: `Runtime Filter`
- Source Heading Path: `Runtime Filter > Configure Runtime Filter | Runtime Filter > Configure Runtime Filter > Runtime Filter mode`
- Source Line Ranges: `234-245`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tiflash`, `sql`
- Topic Tags: `runtime filter`, `system variable`, `mode`, `off`, `local`, `global`, `mpp`, `hash join`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0144_28b6646b2b`
- Source ID: `tidb-docs-8.1:runtime-filter.md#configure-runtime-filter`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a8c4821b469d0ecf757b1fc07ecb32b6559c4035fcb14f33df4a379028f7122a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/runtime-filter#configure-runtime-filter
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/runtime-filter.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the Runtime Filter mode settings, supported values, and the controlling system variable.
- Retrieval Keywords: Configure Runtime Filter, Runtime Filter mode, Filter Sender operator, Filter Receiver operator, OFF, LOCAL, GLOBAL, tidb_runtime_filter_mode, same MPP task, HashJoin operator and TableScan operator are in the same task
- Follow-up Guidance: The source also states that you can configure the mode and predicate type of Runtime Filter.
- Classification Note: This is classified as configuration because the official content defines Runtime Filter modes and states that the system variable tidb_runtime_filter_mode controls them.

## Official Source Content

## Configure Runtime Filter

When using Runtime Filter, you can configure the mode and predicate type of Runtime Filter.
### Runtime Filter mode

The mode of Runtime Filter is the relationship between the **Filter Sender operator** and **Filter Receiver operator**. There are three modes: `OFF`, `LOCAL`, and `GLOBAL`. In v7.3.0, only `OFF` and `LOCAL` modes are supported. The Runtime Filter mode is controlled by the system variable [`tidb_runtime_filter_mode`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_runtime_filter_mode-new-in-v720).

- `OFF`: Runtime Filter is disabled. After it is disabled, the query behavior is the same as in previous versions.
- `LOCAL`: Runtime Filter is enabled in the local mode. In the local mode, the **Filter Sender operator** and **Filter Receiver operator** are in the same MPP task. In other words, Runtime Filter can be applied to the scenario where the HashJoin operator and TableScan operator are in the same task. Currently, Runtime Filter only supports the local mode. To enable this mode, set it to `LOCAL`.
- `GLOBAL`: currently, the global mode is not supported. You cannot set Runtime Filter to this mode.
