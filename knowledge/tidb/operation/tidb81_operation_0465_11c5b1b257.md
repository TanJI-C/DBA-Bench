# Disable resource control across TiDB, TiKV, and TiFlash

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-resource-control.md`
- Source Title: `Use Resource Control to Achieve Resource Isolation`
- Source Heading Path: `Use Resource Control to Achieve Resource Isolation > Disable resource control`
- Source Line Ranges: `487-516`
- Source Scope: `all`
- Primary Component: `tidb`
- Related Components: `tikv`, `tiflash`, `cloud`
- Topic Tags: `resource-control`, `disable`, `global-setting`, `tikv-config`, `tiflash-config`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0465_11c5b1b257`
- Source ID: `tidb-docs-8.1:tidb-resource-control.md#disable-resource-control`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4e661f8062a8506aefdc1ab7467e3b0db29805f14093eb867fd861215cb158fe`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-resource-control#disable-resource-control
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-resource-control.md

## Retrieval Guidance

- Use When: Use this content when retrieving the documented steps and related TiKV and TiFlash settings for disabling resource control.
- Retrieval Keywords: SET GLOBAL tidb_enable_resource_control = 'OFF', tidb_enable_resource_control, resource-control.enabled, enable_resource_control, Disable resource control, TiKV parameter resource-control.enabled, TiFlash configuration item enable_resource_control
- Follow-up Guidance: The content also distinguishes TiDB Self-Managed from TiDB Cloud for `resource-control.enabled` and `enable_resource_control`, noting the TiDB Cloud values are `true` by default and do not support dynamic modification.
- Classification Note: This is classified as operation because the content describes disabling an existing feature across TiDB, TiKV, and TiFlash using a global statement and component configuration items.

## Official Source Content

## Disable resource control

1. Execute the following statement to disable the resource control feature.

    ```sql
    SET GLOBAL tidb_enable_resource_control = 'OFF';
    ```

2. Set the TiKV parameter [`resource-control.enabled`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#resource-control) to `false` to disable scheduling based on the RU of the resource group.

3. Set the TiFlash configuration item [`enable_resource_control`](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-configuration#configure-the-tiflashtoml-file) to `false` to disable TiFlash resource control.

1. Execute the following statement to disable the resource control feature.

    ```sql
    SET GLOBAL tidb_enable_resource_control = 'OFF';
    ```

2. For TiDB Self-Managed, you can use the `resource-control.enabled` parameter to control whether to use request scheduling based on resource group quotas. For TiDB Cloud, the value of the `resource-control.enabled` parameter is `true` by default and does not support dynamic modification. If you need to disable it for TiDB Cloud Dedicated clusters, contact [TiDB Cloud Support](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support).

3. For TiDB Self-Managed, you can use the `enable_resource_control` configuration item to control whether to enable TiFlash resource control. For TiDB Cloud, the value of the `enable_resource_control` parameter is `true` by default and does not support dynamic modification. If you need to disable it for TiDB Cloud Dedicated clusters, contact [TiDB Cloud Support](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support).
