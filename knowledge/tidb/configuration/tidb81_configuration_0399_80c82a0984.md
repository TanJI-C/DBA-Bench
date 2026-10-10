# TiUP topology shared service configuration and component version settings

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-cluster-topology-reference.md`
- Source Title: `Topology Configuration File for TiDB Deployment Using TiUP`
- Source Heading Path: `Topology Configuration File for TiDB Deployment Using TiUP > File structure > `server_configs` | Topology Configuration File for TiDB Deployment Using TiUP > File structure > `component_versions``
- Source Line Ranges: `130-204`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `tidb`, `tikv`, `pd`, `tiflash`, `tiproxy`, `ticdc`, `dashboard`, `shared`
- Topic Tags: `topology-file`, `server-configs`, `component-versions`, `instance-overrides`, `mixed-version`, `configuration-precedence`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0399_80c82a0984`
- Source ID: `tidb-docs-8.1:tiup/tiup-cluster-topology-reference.md#server-configs`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ac26c5ddb92fff91458ab8d8dd7d5baae12d658d75a25b34c04fe7d8a075a323`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-cluster-topology-reference#server-configs
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-cluster-topology-reference.md

## Retrieval Guidance

- Use When: Use this chunk when looking up how `server_configs` defines shared component configuration and how `component_versions` pins versions for components in a TiUP topology file.
- Retrieval Keywords: server_configs, component_versions, topology configuration file, configuration precedence, instance overrides, mixed-version deployment scenario, tidb, tikv, pd, tiflash, tiflash_learner, tiproxy, pump, drainer, cdc, kvcdc, tidb_dashboard, prometheus, grafana, alertmanager
- Follow-up Guidance: The content notes that when `component_versions` is configured, the specified version is also used in subsequent cluster scaling and upgrade operations.
- Classification Note: This is classified as configuration because the content defines topology YAML sections, shared service settings, and component version fields including override behavior.

## Official Source Content

### `server_configs`

`server_configs` is used to configure services and to generate configuration files for each component. Similar to the `global` section, the configuration of this section can be overwritten by the configurations with the same names in an instance. `server_configs` mainly includes the following fields:

- `tidb`: TiDB service-related configuration. For the complete configuration, see [TiDB configuration file](https://docs.pingcap.com/tidb/stable/tidb-configuration-file).

- `tikv`: TiKV service-related configuration. For the complete configuration, see [TiKV configuration file](https://docs.pingcap.com/tidb/stable/tikv-configuration-file).

- `pd`: PD service-related configuration. For the complete configuration, see [PD configuration file](https://docs.pingcap.com/tidb/stable/pd-configuration-file).

- `tiflash`: TiFlash service-related configuration. For the complete configuration, see [TiFlash configuration file](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-configuration).

- `tiflash_learner`: Each TiFlash node has a special built-in TiKV. This configuration item is used to configure this special TiKV. It is generally not recommended to modify the content under this configuration item.

- `tiproxy`: TiProxy service-related configuration. For the complete configuration, see [TiProxy configuration file](https://docs.pingcap.com/tidb/stable/tiproxy/tiproxy-configuration).

- `pump`: Pump service-related configuration. For the complete configuration, see [TiDB Binlog configuration file](https://docs.pingcap.com/tidb/stable/tidb-binlog/tidb-binlog-configuration-file#pump).

- `drainer`: Drainer service-related configuration. For the complete configuration, see [TiDB Binlog configuration file](https://docs.pingcap.com/tidb/stable/tidb-binlog/tidb-binlog-configuration-file#drainer).

- `cdc`: TiCDC service-related configuration. For the complete configuration, see [Deploy TiCDC](https://docs.pingcap.com/tidb/stable/ticdc/deploy-ticdc).

A `server_configs` configuration example is as follows:

```yaml
server_configs:
  tidb:
    lease: "45s"
    split-table: true
    token-limit: 1000
    instance.tidb_enable_ddl: true
  tikv:
    log-level: "info"
    readpool.unified.min-thread-count: 1
```

The above configuration specifies the global configuration of TiDB and TiKV.
### `component_versions`

> **Note:**
>
> For components that share a version number, such as TiDB, TiKV, PD, and TiCDC, there are no complete tests to ensure that they work properly in a mixed-version deployment scenario. Ensure that you use this section only in test environments, or with the help of [technical support](https://docs.pingcap.com/tidb/stable/support).

`component_versions` is used to specify the version number of a certain component. 

- When `component_versions` is not configured, each component either uses the same version number as the TiDB cluster (such as PD and TiKV), or uses the latest version (such as Alertmanager). 
- When `component_versions` is configured, the corresponding component will use the specified version, and this version will be used in subsequent cluster scaling and upgrade operations. 

Make sure you only configure it when you need to use a specific version of a component. 

`component_versions` contains the following fields:

- `tikv`: The version of the TiKV component
- `tiflash`: The version of the TiFlash component
- `pd`: The version of the PD component
- `tidb_dashboard`: The version of the standalone TiDB Dashboard component
- `pump`: The version of the Pump component
- `drainer`: The version of the Drainer component
- `cdc`: The version of the CDC component
- `kvcdc`: The version of the TiKV-CDC component
- `tiproxy`: The version of the TiProxy component
- `prometheus`: The version of the Prometheus component
- `grafana`: The version of the Grafana component
- `alertmanager`: The version of the Alertmanager component

The following is an example configuration for `component_versions`:

```yaml
component_versions:
  kvcdc: "v1.1.1"
```

The preceding configuration specifies the version number of TiKV-CDC to be `v1.1.1`.
