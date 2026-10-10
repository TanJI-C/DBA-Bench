# Resource control parameters and enablement combinations

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-resource-control.md`
- Source Title: `Use Resource Control to Achieve Resource Isolation`
- Source Heading Path: `Use Resource Control to Achieve Resource Isolation > Parameters for resource control`
- Source Line Ranges: `102-142`
- Source Scope: `all`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `tiflash`, `cloud`
- Topic Tags: `resource-control`, `system-variables`, `configuration`, `flow-control`, `request-scheduling`, `tiflash`, `ru`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0348_f2967c3d25`
- Source ID: `tidb-docs-8.1:tidb-resource-control.md#parameters-for-resource-control`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2a698549e2bbe4416147b855464403957f6f385c1351e3ce23ae175faff3e2bb`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-resource-control#parameters-for-resource-control
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-resource-control.md

## Retrieval Guidance

- Use When: Use this chunk when looking for which resource control variables and configuration items enable flow control, request scheduling, or TiFlash resource control and how their combinations behave.
- Retrieval Keywords: tidb_enable_resource_control, resource-control.enabled, enable_resource_control, Parameters for resource control, flow control and scheduling, Invalid combination, The feature is disabled, TiFlash resource control, Pipeline execution model, resource groups, request scheduling based on resource groups
- Follow-up Guidance: The chunk also points to RFC: Global Resource Control in TiDB and TiFlash Resource Control for more information about the mechanism and parameters.
- Classification Note: This is configuration content because it defines the system variables and parameters for TiDB, TiKV, and TiFlash, plus the enablement combination outcomes.

## Official Source Content

## Parameters for resource control

The resource control feature introduces the following system variables or parameters:

* TiDB: you can use the [`tidb_enable_resource_control`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_resource_control-new-in-v660) system variable to control whether to enable flow control for resource groups.

* TiKV: you can use the [`resource-control.enabled`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#resource-control) parameter to control whether to use request scheduling based on resource groups.
* TiFlash: you can use the [`tidb_enable_resource_control`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_resource_control-new-in-v660) system variable and the [`enable_resource_control`](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-configuration#configure-the-tiflashtoml-file) configuration item (introduced in v7.4.0) to control whether to enable TiFlash resource control.

* TiKV: For TiDB Self-Managed, you can use the `resource-control.enabled` parameter to control whether to use request scheduling based on resource group quotas. For TiDB Cloud, the value of the `resource-control.enabled` parameter is `true` by default and does not support dynamic modification.
* TiFlash: For TiDB Self-Managed, you can use the `tidb_enable_resource_control` system variable and the `enable_resource_control` configuration item (introduced in v7.4.0) to control whether to enable TiFlash resource control.

Starting from TiDB v7.0.0, `tidb_enable_resource_control` and `resource-control.enabled` are enabled by default. The results of the combinations of these two parameters are shown in the following table.

| `resource-control.enabled`  | `tidb_enable_resource_control`= ON   | `tidb_enable_resource_control`= OFF  |
|:----------------------------|:-------------------------------------|:-------------------------------------|
| `resource-control.enabled`= true  |  Flow control and scheduling (recommended) | Invalid combination      |
| `resource-control.enabled`= false |  Only flow control (not recommended)                 | The feature is disabled. |

Starting from v7.4.0, the TiFlash configuration item `enable_resource_control` is enabled by default. It works together with `tidb_enable_resource_control` to control the TiFlash resource control feature. TiFlash resource control only performs flow control and priority scheduling when both `enable_resource_control` and `tidb_enable_resource_control` are enabled. Additionally, when `enable_resource_control` is enabled, TiFlash uses the [Pipeline execution model](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-pipeline-model).

Starting from v7.4.0, the TiFlash configuration item `enable_resource_control` is enabled by default. It works together with `tidb_enable_resource_control` to control the TiFlash resource control feature. TiFlash resource control only performs flow control and priority scheduling when both `enable_resource_control` and `tidb_enable_resource_control` are enabled. Additionally, when `enable_resource_control` is enabled, TiFlash uses the [Pipeline execution model](http://docs.pingcap.com/tidb/dev/tiflash-pipeline-model).

For more information about the resource control mechanism and parameters, see [RFC: Global Resource Control in TiDB](https://github.com/pingcap/tidb/blob/release-8.1/docs/design/2022-11-25-global-resource-control.md) and [TiFlash Resource Control](https://github.com/pingcap/tiflash/blob/release-8.1/docs/design/2023-09-21-tiflash-resource-control.md).
