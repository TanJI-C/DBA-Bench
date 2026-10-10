# Scale-in options and output

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-component-cluster-scale-in.md`
- Source Title: `tiup cluster scale-in`
- Source Heading Path: `tiup cluster scale-in > Options | tiup cluster scale-in > Options > -N, --node | tiup cluster scale-in > Options > --force | tiup cluster scale-in > Options > --transfer-timeout | tiup cluster scale-in > Options > -h, --help | tiup cluster scale-in > Output`
- Source Line Ranges: `37-75`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `pd`, `tikv`, `tiflash`
- Topic Tags: `options`, `node-selection`, `force-removal`, `transfer-timeout`, `help`, `output`, `data-loss-warning`, `leader-transfer`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_1012_628da2a24a`
- Source ID: `tidb-docs-8.1:tiup/tiup-component-cluster-scale-in.md#options`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `65b4f96d95005520c5e5953cc99ab967980213a32467d3e4a8f94183ecb151c8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-scale-in#options
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-component-cluster-scale-in.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the `tiup cluster scale-in` options, including node selection, forced removal, leader transfer timeout, help, warning details, and what output the command shows.
- Retrieval Keywords: -N, --node, --force, --transfer-timeout, -h, --help, tiup cluster scale-in options, forcibly remove the specified nodes, data loss warning, PD or TiKV leader transfer, 600 seconds, shows the logs of the scaling-in process, multiple nodes are separated by commas
- Follow-up Guidance: The content notes that if a PD or TiKV node is taken offline directly without waiting for leader transfer to complete, service performance might jitter.
- Classification Note: This is classified as a reference chunk because the official content enumerates command options, their data types and defaults, warnings, notes, and output behavior.

## Official Source Content

## Options
### -N, --node

- Specifies the nodes to take down. Multiple nodes are separated by commas.
- Data type: `STRING`
- There is no default value. This option is mandatory and the value must be not null.
### --force

- Controls whether to forcibly remove the specified nodes from the cluster. Sometimes, the host of the node to take offline might be down, which makes it impossible to connect to the node via SSH for operations, so you can forcibly remove the node from the cluster using the `--force` option.
- Data type: `BOOLEAN`
- This option is disabled by default with the `false` value. To enable this option, add this option to the command, and either pass the `true` value or do not pass any value.

> **Warning:**
>
> When you use this option to forcibly remove TiKV or TiFlash nodes that are in service or are pending offline, these nodes will be deleted immediately without waiting for data to be migrated. This imposes a very high risk of data loss. If data loss occurs in the region where the metadata is located, the entire cluster will be unavailable and unrecoverable.
### --transfer-timeout

- When a PD or TiKV node is to be removed, the Region leader on the node will be transferred to another node first. Because the transferring process takes some time, you can set the maximum waiting time (in seconds) by configuring `--transfer-timeout`. After the timeout, the `tiup cluster scale-in` command skips waiting and starts the scaling-in directly.
- Data type: `UINT`
- The option is enabled by default with `600` seconds (the default value) passed in.

> **Note:**
>
> If a PD or TiKV node is taken offline directly without waiting for the leader transfer to be completed, the service performance might jitter.
### -h, --help

- Prints the help information.
- Data type: `BOOLEAN`
- This option is disabled by default with the `false` value. To enable this option, add this option to the command, and either pass the `true` value or do not pass any value.
## Output

Shows the logs of the scaling-in process.

[<< Back to the previous page - TiUP Cluster command list](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster#command-list)
