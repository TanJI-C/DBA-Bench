# TiFlash overview and PD scheduling parameters

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiflash/tiflash-configuration.md`
- Source Title: `Configure TiFlash`
- Source Heading Path: `Configure TiFlash | Configure TiFlash > PD scheduling parameters`
- Source Line Ranges: `5-31`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: `tiflash`, `tiup`, `tikv`
- Topic Tags: `pd-ctl`, `scheduling`, `replica-management`, `store-limit`, `topology-labels`, `placement-rules`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0352_1ce1b2a098`
- Source ID: `tidb-docs-8.1:tiflash/tiflash-configuration.md#configure-tiflash`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c8b3f690e9edc47941afd25ef6bb0026b26fa51b3bb27c22a096afd7c1aee28c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiflash/tiflash-configuration#configure-tiflash
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiflash/tiflash-configuration.md

## Retrieval Guidance

- Use When: Use this chunk when looking for PD scheduling parameters and pd-ctl commands related to TiFlash replica management, store scheduling rate, or placement rules configuration.
- Retrieval Keywords: PD scheduling parameters, pd-ctl, tiup ctl:v<CLUSTER_VERSION> pd, replica-schedule-limit, region-schedule-limit, store-balance-rate, store limit, pd-ctl -u <pd_ip:pd_port> store limit <store_id> <value>, pd-ctl -u <pd_ip:pd_port> store, pd-ctl -u <pd_ip:pd_port> store limit, replication.location-labels, pd-ctl config placement-rules, geo-distributed-deployment-topology
- Follow-up Guidance: The content notes that `store-balance-rate` is deprecated since v4.0.2 and points to `store-limit` for details.
- Classification Note: This is configuration content for the PD component because it describes PD scheduling parameters and related pd-ctl settings used with TiFlash.

## Official Source Content

# Configure TiFlash

This document introduces the configuration parameters related to the deployment and use of TiFlash.
## PD scheduling parameters

You can adjust the PD scheduling parameters using [pd-ctl](https://docs.pingcap.com/tidb/stable/pd-control). Note that you can use `tiup ctl:v<CLUSTER_VERSION> pd` to replace `pd-ctl -u <pd_ip:pd_port>` when using tiup to deploy and manage your cluster.

- [`replica-schedule-limit`](https://docs.pingcap.com/tidb/stable/pd-configuration-file#replica-schedule-limit): determines the rate at which the replica-related operator is generated. The parameter affects operations such as making nodes offline and add replicas.

  > **Note:**
  >
  > The value of this parameter should be less than that of `region-schedule-limit`. Otherwise, the normal Region scheduling among TiKV nodes is affected.

- `store-balance-rate`: limits the rate at which Regions of each TiKV/TiFlash store are scheduled. Note that this parameter takes effect only when the stores have newly joined the cluster. If you want to change the setting for existing stores, use the following command.

  > **Note:**
  >
  > Since v4.0.2, the `store-balance-rate` parameter has been deprecated and changes have been made to the `store limit` command. See [store-limit](https://docs.pingcap.com/tidb/stable/configure-store-limit) for details.

    - Execute the `pd-ctl -u <pd_ip:pd_port> store limit <store_id> <value>` command to set the scheduling rate of a specified store. (To get `store_id`, you can execute the `pd-ctl -u <pd_ip:pd_port> store` command.
    - If you do not set the scheduling rate for Regions of a specified store, this store inherits the setting of `store-balance-rate`.
    - You can execute the `pd-ctl -u <pd_ip:pd_port> store limit` command to view the current setting value of `store-balance-rate`.

- [`replication.location-labels`](https://docs.pingcap.com/tidb/stable/pd-configuration-file#location-labels): indicates the topological relationship of TiKV instances. The order of the keys indicates the layering relationship of different labels. If TiFlash is enabled, you need to use [`pd-ctl config placement-rules`](https://docs.pingcap.com/tidb/stable/pd-control#config-show--set-option-value--placement-rules) to set the default value. For details, see [geo-distributed-deployment-topology](https://docs.pingcap.com/tidb/stable/geo-distributed-deployment-topology).
