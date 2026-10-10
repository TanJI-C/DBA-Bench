# Load Base Split overview, principles, and configuration usage

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/configure-load-base-split.md`
- Source Title: `Load Base Split`
- Source Heading Path: `Load Base Split | Load Base Split > Scenarios | Load Base Split > Implementation principles | Load Base Split > Usage`
- Source Line Ranges: `5-88`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `pd`, `sql`
- Topic Tags: `hotspot`, `region-split`, `read-load`, `qps-threshold`, `byte-threshold`, `cpu-threshold`, `configuration`, `sql-config`, `tikv-api`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0022_38fb2ee9ec`
- Source ID: `tidb-docs-8.1:configure-load-base-split.md#load-base-split`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `04b9fa665079505fc7a3e3158b5731fce0aabf1619b9cfe1001955f3a937a69d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/configure-load-base-split#load-base-split
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/configure-load-base-split.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about TiKV Load Base Split for hotspot Regions, its triggering conditions, or how to view or modify its thresholds.
- Retrieval Keywords: Load Base Split, split.qps-threshold, split.byte-threshold, split.region-cpu-overload-threshold-ratio, region-split-size, Region hotspot, full table scans, index lookups for small tables, Unified Read Pool, QPS threshold, byte threshold, CPU usage threshold, SET config tikv, show config where type='tikv' and name like '%split.qps-threshold%';, curl -X POST "http://ip:status_port/config", MergeChecker
- Follow-up Guidance: The source also provides the exact default threshold values, the 10 consecutive seconds condition, and SQL and TiKV API examples to set or view the configuration.
- Classification Note: This is classified as a TiKV configuration topic because the content explains the Load Base Split feature behavior and the specific TiKV configuration parameters and commands used to control it.

## Official Source Content

# Load Base Split

Load Base Split is a new feature introduced in TiDB 4.0. It aims to solve the hotspot issue caused by unbalanced access between Regions, such as full table scans for small tables.
## Scenarios

In TiDB, it is easy to generate hotspots when the load is concentrated on certain nodes. PD tries to schedule the hot Regions so that they are distributed as evenly as possible across all nodes for better performance.

However, the minimum unit for PD scheduling is Region. If the number of hotspots in a cluster is smaller than the number of nodes, or if a few hotspots have far more load than other Regions, PD can only move the hotspot from one node to another, but not make the entire cluster share the load.

This scenario is especially common with workloads that are mostly read requests, such as full table scans and index lookups for small tables, or frequent access to some fields.

Previously, the solution to this problem was to manually execute a command to split one or more hotspot Regions, but this approach has two problems:

- Evenly splitting a Region is not always the best choice, because requests might be concentrated on a few keys. In such cases, hotspots might still be on one of the Regions after evenly splitting, and it might take multiple even splits to realize the goal.
- Human intervention is not timely or simple.
## Implementation principles

Load Base Split automatically splits the Region based on statistics. It identifies the Regions whose read load or CPU usage consistently exceeds the threshold for 10 seconds, and splits these Regions at a proper position. When choosing the split position, Load Base Split tries to balance the access load of both Regions after the split and avoid access across Regions.

The Region split by Load Base Split will not be merged quickly. On the one hand, PD's `MergeChecker` skips the hot Regions; on the other hand, PD also determines whether to merge two Regions according to `QPS` in the heartbeat information, to avoid the merging of two Regions with high `QPS`.
## Usage

The Load Base Split feature is currently controlled by the following parameters:

- [`split.qps-threshold`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#qps-threshold): The QPS threshold at which a Region is identified as a hotspot. The default value is `3000` per second when [`region-split-size`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#region-split-size) is less than 4 GB; otherwise the default value is `7000`.
- [`split.byte-threshold`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#byte-threshold-new-in-v50): (Introduced in v5.0) The traffic threshold at which a Region is identified as a hotspot. The unit is byte. The default value is 30 MiB per second when `region-split-size` is less than 4 GB; otherwise the default value is 100 MiB per second.
- [`split.region-cpu-overload-threshold-ratio`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#region-cpu-overload-threshold-ratio-new-in-v620): (Introduced in v6.2.0) The CPU usage threshold (the percentage of CPU time of the read thread pool) at which a Region is identified as a hotspot. The default value is `0.25` when `region-split-size` is less than 4 GB; otherwise the default value is `0.75`.

If a Region meets one of the following conditions for 10 consecutive seconds, TiKV tries to split the Region:

- the sum of its read requests exceeds `split.qps-threshold`.
- its traffic exceeds `split.byte-threshold`.
- its CPU usage in the Unified Read Pool exceeds `split.region-cpu-overload-threshold-ratio`.

Load Base Split is enabled by default, but the parameter is set to a rather high value. If you want to disable this feature, set `split.qps-threshold` and `split.byte-threshold` high enough and set `split.region-cpu-overload-threshold-ratio` to `0` at the same time.

To modify the parameter, take either of the following two methods:

- Use a SQL statement:

    ```sql
    # Set the QPS threshold to 1500
    SET config tikv split.qps-threshold=1500;
    # Set the byte threshold to 15 MiB (15 * 1024 * 1024)
    SET config tikv split.byte-threshold=15728640;
    # Set the CPU usage threshold to 50%
    SET config tikv split.region-cpu-overload-threshold-ratio=0.5;
    ```

- Use TiKV:

    ```shell
    curl -X POST "http://ip:status_port/config" -H "accept: application/json" -d '{"split.qps-threshold":"1500"}'
    curl -X POST "http://ip:status_port/config" -H "accept: application/json" -d '{"split.byte-threshold":"15728640"}'
    curl -X POST "http://ip:status_port/config" -H "accept: application/json" -d '{"split.region-cpu-overload-threshold-ratio":"0.5"}'
    ```

Accordingly, you can view the configuration by either of the following two methods:

- Use a SQL statement:

    ```sql
    show config where type='tikv' and name like '%split.qps-threshold%';
    ```

- Use TiKV:

    ```shell
    curl "http://ip:status_port/config"
    ```

> **Note:**
>
> Starting from v4.0.0-rc.2, you can modify and view the configuration using SQL statements.
