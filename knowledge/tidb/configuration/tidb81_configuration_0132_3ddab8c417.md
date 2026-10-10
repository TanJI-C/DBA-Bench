# PD controller resource control and request unit settings

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/pd-configuration-file.md`
- Source Title: `PD Configuration File`
- Source Heading Path: `PD Configuration File > controller | PD Configuration File > controller > `degraded-mode-wait-duration` | PD Configuration File > controller > `request-unit` | PD Configuration File > controller > `request-unit` > `read-base-cost` | PD Configuration File > controller > `request-unit` > `write-base-cost` | PD Configuration File > controller > `request-unit` > `read-cost-per-byte` | PD Configuration File > controller > `request-unit` > `write-cost-per-byte` | PD Configuration File > controller > `request-unit` > `read-cpu-ms-cost``
- Source Line Ranges: `535-575`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: `tidb`
- Topic Tags: `resource-control`, `degraded-mode`, `request-unit`, `ru`, `read-cost`, `write-cost`, `cpu-cost`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0132_3ddab8c417`
- Source ID: `tidb-docs-8.1:pd-configuration-file.md#controller`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `07bfe42eaa645885f37a9d6d09ea8e2ddd78a8a4c82c5b0b1e2368e9cf3324ec`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/pd-configuration-file#controller
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/pd-configuration-file.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving PD Resource Control configuration for degraded mode timing or Request Unit cost conversion factors such as read, write, byte, and CPU costs.
- Retrieval Keywords: controller, Resource Control, degraded-mode-wait-duration, degradation mode, Local Token Bucket, LTB, Global Token Bucket, GTB, request-unit, Request Unit, RU, read-base-cost, write-base-cost, read-cost-per-byte, write-cost-per-byte, read-cpu-ms-cost, 1 RU = 64 KiB read bytes, 1 RU = 1 KiB write bytes, 1 RU = 3 millisecond CPU time
- Follow-up Guidance: The source links to TiDB Resource Control and What is Request Unit (RU) for related details.
- Classification Note: This is classified as PD configuration because the content defines the `controller` section and its built-in Resource Control and RU conversion settings in PD.

## Official Source Content

## controller

This section describes the configuration items that are built into PD for [Resource Control](https://docs.pingcap.com/tidb/stable/tidb-resource-control).
### `degraded-mode-wait-duration`

+ Time to wait to trigger the degradation mode. Degradation mode means that when the Local Token Bucket (LTB) and Global Token Bucket (GTB) are lost, the LTB falls back to the default resource group configuration and no longer has a GTB authorization token, thus ensuring that the service is not affected in the event of network isolation or anomalies.
+ Default value: 0s
+ The degradation mode is disabled by default.
### `request-unit`

The following are the configuration items about the [Request Unit (RU)](https://docs.pingcap.com/tidb/stable/tidb-resource-control#what-is-request-unit-ru).
#### `read-base-cost`

+ Basis factor for conversion from a read request to RU
+ Default value: 0.125
#### `write-base-cost`

+ Basis factor for conversion from a write request to RU
+ Default value: 1
#### `read-cost-per-byte`

+ Basis factor for conversion from read flow to RU
+ Default value: 1/(64 * 1024)
+ 1 RU = 64 KiB read bytes
#### `write-cost-per-byte`

+ Basis factor for conversion from write flow to RU
+ Default value: 1/1024
+ 1 RU = 1 KiB write bytes
#### `read-cpu-ms-cost`

+ Basis factor for conversion from CPU to RU
+ Default value: 1/3
+ 1 RU = 3 millisecond CPU time
