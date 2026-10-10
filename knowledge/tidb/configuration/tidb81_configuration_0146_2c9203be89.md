# Configure PD location-labels and isolation-level

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/schedule-replicas-by-topology-labels.md`
- Source Title: `Schedule Replicas by Topology Labels`
- Source Heading Path: `Schedule Replicas by Topology Labels > Configure `location-labels` for PD | Schedule Replicas by Topology Labels > Configure `isolation-level` for PD`
- Source Line Ranges: `217-275`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: `tikv`, `tidb`
- Topic Tags: `location-labels`, `isolation-level`, `pd-ctl`, `replica-scheduling`, `topology-awareness`, `placement-rules`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0146_2c9203be89`
- Source ID: `tidb-docs-8.1:schedule-replicas-by-topology-labels.md#configure-location-labels-for-pd`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `dd35a9edd6e031bc8f9e9d077912e78ab5632bc9a63d219ff105a005b5a5b73e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/schedule-replicas-by-topology-labels#configure-location-labels-for-pd
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/schedule-replicas-by-topology-labels.md

## Retrieval Guidance

- Use When: Use this chunk when looking for how PD interprets topology through `location-labels` and how to enforce minimum replica isolation with `isolation-level`.
- Retrieval Keywords: location-labels, isolation-level, PD, [replication], pd-ctl config set location-labels zone,rack,host, pd-ctl config set isolation-level zone, zone, rack, host, replica scheduling, topology, Placement Rules in SQL
- Follow-up Guidance: This content also states that `location-labels` must be configured together with TiKV `labels`, and that Placement Rules in SQL is incompatible with PD `location-labels` and ignores that configuration.
- Classification Note: The classification is configuration because the content defines PD settings and pd-ctl commands for `location-labels` and `isolation-level` that control topology-aware replica scheduling.

## Official Source Content

## Configure `location-labels` for PD

According to the description above, the label can be any key-value pair used to describe TiKV attributes. But PD cannot identify the location-related labels and the layer relationship of these labels. Therefore, you need to make the following configuration for PD to understand the TiKV node topology.

Defined as an array of strings, `location-labels` is the configuration for PD. Each item of this configuration corresponds to the key of TiKV `labels`. Besides, the sequence of each key represents the layer relationship of different labels (the isolation levels decrease from left to right).

You can customize the value of `location-labels`, such as `zone`, `rack`, or `host`, because the configuration does not have default values. Also, this configuration has **no** restriction in the number of label levels (not mandatory for 3 levels) as long as they match with TiKV server labels.

> **Note:**
>
> - To make configurations take effect, you must configure `location-labels` for PD and `labels` for TiKV at the same time. Otherwise, PD does not perform scheduling according to the topology.
> - If you use Placement Rules in SQL, you only need to configure `labels` for TiKV. Currently, Placement Rules in SQL is incompatible with the `location-labels` configuration of PD and ignores this configuration. It is not recommended to use `location-labels` and Placement Rules in SQL at the same time; otherwise, unexpected results might occur.

To configure `location-labels`, choose one of the following methods according to your cluster situation:

+ If the PD cluster is not initialized, configure `location-labels` in the PD configuration file:

    ```toml
    [replication]
    location-labels = ["zone", "rack", "host"]
    ```

+ If the PD cluster is already initialized, use the pd-ctl tool to make online changes:

    ```bash
    pd-ctl config set location-labels zone,rack,host
    ```
## Configure `isolation-level` for PD

If `location-labels` has been configured, you can further enhance the topological isolation requirements on TiKV clusters by configuring `isolation-level` in the PD configuration file.

Assume that you have made a three-layer cluster topology by configuring `location-labels` according to the instructions above: zone -> rack -> host, you can configure the `isolation-level` to `zone` as follows:

```toml
[replication]
isolation-level = "zone"
```

If the PD cluster is already initialized, you need to use the pd-ctl tool to make online changes:

```bash
pd-ctl config set isolation-level zone
```

The `location-level` configuration is an array of strings, which needs to correspond to a key of `location-labels`. This parameter limits the minimum and mandatory isolation level requirements on TiKV topology clusters.

> **Note:**
>
> `isolation-level` is empty by default, which means there is no mandatory restriction on the isolation level. To set it, you need to configure `location-labels` for PD and ensure that the value of `isolation-level` is one of `location-labels` names.
