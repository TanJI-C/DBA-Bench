# TiDB Binlog deployment topology, templates, and key parameters

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-binlog-deployment-topology.md`
- Source Title: `TiDB Binlog Deployment Topology`
- Source Heading Path: `TiDB Binlog Deployment Topology | TiDB Binlog Deployment Topology > Topology information | TiDB Binlog Deployment Topology > Topology information > Topology templates | TiDB Binlog Deployment Topology > Topology information > Key parameters`
- Source Line Ranges: `5-57`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `tidb`, `pd`, `tikv`
- Topic Tags: `topology`, `binlog`, `deployment`, `templates`, `parameters`, `downstream`, `pump`, `drainer`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0195_b91f364eff`
- Source ID: `tidb-docs-8.1:tidb-binlog-deployment-topology.md#tidb-binlog-deployment-topology`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `abdcb622b62ab2b41a9af95cdc27a68831d2cbb83fcbab03aaedd418566ef395`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-binlog-deployment-topology#tidb-binlog-deployment-topology
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-binlog-deployment-topology.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB Binlog deployment topology examples, topology templates, or key TiUP topology configuration parameters for Pump and Drainer in a minimal TiDB topology.
- Retrieval Keywords: TiDB Binlog deployment topology, Topology templates, simple-tidb-binlog.yaml, simple-file-binlog.yaml, complex-tidb-binlog.yaml, server_configs.tidb.binlog.enable, server_configs.tidb.binlog.ignore-error, drainer_servers.config.syncer.db-type, drainer_servers.config.syncer.to, enable_binlog, ignore-error, Pump, Drainer, mysql as the downstream type, file as the downstream type, tidb_server_critical_error_total, Set GC time to 7 days, default initialization commitTS -1, 10.0.1.12:4000, Topology Configuration File for Deploying TiDB Using TiUP
- Follow-up Guidance: For detailed descriptions of the configuration items in the topology file, the source points to Topology Configuration File for Deploying TiDB Using TiUP and to TiDB Binlog Configuration File for syncer.to details.
- Classification Note: This is classified as self-managed TiUP configuration content because the source defines deployment topology, templates, instance layout, and exact topology file parameters for TiDB Binlog components.

## Official Source Content

# TiDB Binlog Deployment Topology

This document describes the deployment topology of [TiDB Binlog](https://docs.pingcap.com/tidb/stable/tidb-binlog/tidb-binlog-overview) based on the minimal TiDB topology.

TiDB Binlog is the widely used component for replicating incremental data. It provides near real-time backup and replication.
## Topology information

| Instance | Count | Physical machine configuration | IP | Configuration |
| :-- | :-- | :-- | :-- | :-- |
| TiDB | 3 | 16 VCore 32 GB | 10.0.1.1 <br/> 10.0.1.2 <br/> 10.0.1.3 | Default port configuration; <br/> Enable `enable_binlog`; <br/> Enable `ignore-error` |
| PD | 3 | 4 VCore 8 GB | 10.0.1.4 <br/> 10.0.1.5 <br/> 10.0.1.6 | Default port configuration |
| TiKV | 3 | 16 VCore 32 GB | 10.0.1.7 <br/> 10.0.1.8 <br/> 10.0.1.9 | Default port configuration |
| Pump| 3 | 8 VCore 16GB | 10.0.1.1 <br/> 10.0.1.7 <br/> 10.0.1.8 | Default port configuration; <br/> Set GC time to 7 days |
| Drainer | 1 | 8 VCore 16GB | 10.0.1.12 | Default port configuration; <br/> Set the default initialization commitTS -1 as the latest timestamp; <br/> Configure the downstream target TiDB as `10.0.1.12:4000` |
### Topology templates

- [The simple template for the TiDB Binlog topology (with `mysql` as the downstream type)](https://github.com/pingcap/docs/blob/master/config-templates/simple-tidb-binlog.yaml)
- [The simple template for the TiDB Binlog topology (with `file` as the downstream type)](https://github.com/pingcap/docs/blob/master/config-templates/simple-file-binlog.yaml)
- [The complex template for the TiDB Binlog topology](https://github.com/pingcap/docs/blob/master/config-templates/complex-tidb-binlog.yaml)

For detailed descriptions of the configuration items in the above TiDB cluster topology file, see [Topology Configuration File for Deploying TiDB Using TiUP](https://docs.pingcap.com/tidb/stable/tiup/tiup-cluster-topology-reference).
### Key parameters

The key parameters in the topology configuration templates are as follows:

- `server_configs.tidb.binlog.enable: true`

    - Enables the binlog service.
    - Default value: `false`.

- `server_configs.tidb.binlog.ignore-error: true`

    - It is recommended to enable this configuration in high availability scenarios.
    - If set to `true`, when an error occurs, TiDB stops writing data into binlog, and adds `1` to the value of the `tidb_server_critical_error_total` monitoring metric.
    - If set to `false`, when TiDB fails to write data into binlog, the whole TiDB service is stopped.

- `drainer_servers.config.syncer.db-type`

    The downstream type of TiDB Binlog. Currently, `mysql`, `tidb`, `kafka`, and `file` are supported.

- `drainer_servers.config.syncer.to`

    The downstream configuration of TiDB Binlog. Depending on different `db-type`s, you can use this configuration item to configure the connection parameters of the downstream database, the connection parameters of Kafka, and the file save path. For details, refer to [TiDB Binlog Configuration File](https://docs.pingcap.com/tidb/stable/tidb-binlog/tidb-binlog-configuration-file#syncerto).

> **Note:**
>
> - When editing the configuration file template, if you do not need custom ports or directories, modify the IP only.
> - You do not need to manually create the `tidb` user in the configuration file. The TiUP cluster component automatically creates the `tidb` user on the target machines. You can customize the user, or keep the user consistent with the control machine.
> - If you configure the deployment directory as a relative path, the cluster will be deployed in the home directory of the user.
