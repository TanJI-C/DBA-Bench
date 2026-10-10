# Initialize TiUP cluster topology file and templates

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/production-deployment-using-tiup.md`
- Source Title: `Deploy a TiDB Cluster Using TiUP`
- Source Heading Path: `Deploy a TiDB Cluster Using TiUP > Step 3. Initialize cluster topology file`
- Source Line Ranges: `229-313`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `pd`, `tidb`, `tikv`, `tiflash`, `ticdc`, `shared`
- Topic Tags: `topology`, `configuration-file`, `templates`, `hybrid-deployment`, `geo-distributed`, `server-configs`, `node-configs`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0140_c9d9191400`
- Source ID: `tidb-docs-8.1:production-deployment-using-tiup.md#step-3-initialize-cluster-topology-file`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c8971c0cbdeb3ecd134a5a4fd4a2ca47ec64b36bd4ffbf53f592b2404fa835d2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/production-deployment-using-tiup#step-3-initialize-cluster-topology-file
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/production-deployment-using-tiup.md

## Retrieval Guidance

- Use When: Use this chunk when you need the TiUP cluster topology initialization commands, example `topology.yaml` structure, or references to topology templates for hybrid, geo-distributed, TiFlash, TiCDC, TiDB Binlog, TiSpark, or minimal deployments.
- Retrieval Keywords: tiup cluster template > topology.yaml, tiup cluster template --full > topology.yaml, tiup cluster template --multi-dc > topology.yaml, topology.yaml, global, server_configs, pd_servers, tidb_servers, tikv_servers, monitoring_servers, grafana_servers, alertmanager_servers, Hybrid Deployment Topology, Geo-Distributed Deployment Topology, server_configs section, config of this node, log.slow-threshold, TiUP configuration template, config.toml.example
- Follow-up Guidance: The content also points to common topology templates and explains that globally effective parameters belong in `server_configs` while node-specific parameters belong in each node `config`.
- Classification Note: This is classified as configuration because the official content centers on creating and editing `topology.yaml`, choosing deployment templates, and placing component parameters in the correct configuration sections.

## Official Source Content

## Step 3. Initialize cluster topology file

Run the following command to create a cluster topology file:

```shell
tiup cluster template > topology.yaml
```

In the following two common scenarios, you can generate recommended topology templates by running commands:

- For hybrid deployment: Multiple instances are deployed on a single machine. For details, see [Hybrid Deployment Topology](https://docs.pingcap.com/tidb/stable/hybrid-deployment-topology).

    ```shell
    tiup cluster template --full > topology.yaml
    ```

- For geo-distributed deployment: TiDB clusters are deployed in geographically distributed data centers. For details, see [Geo-Distributed Deployment Topology](https://docs.pingcap.com/tidb/stable/geo-distributed-deployment-topology).

    ```shell
    tiup cluster template --multi-dc > topology.yaml
    ```

Run `vi topology.yaml` to see the configuration file content:

```shell
global:
  user: "tidb"
  ssh_port: 22
  deploy_dir: "/tidb-deploy"
  data_dir: "/tidb-data"
server_configs: {}
pd_servers:
  - host: 10.0.1.4
  - host: 10.0.1.5
  - host: 10.0.1.6
tidb_servers:
  - host: 10.0.1.7
  - host: 10.0.1.8
  - host: 10.0.1.9
tikv_servers:
  - host: 10.0.1.1
  - host: 10.0.1.2
  - host: 10.0.1.3
monitoring_servers:
  - host: 10.0.1.4
grafana_servers:
  - host: 10.0.1.4
alertmanager_servers:
  - host: 10.0.1.4
```

The following examples cover seven common scenarios. You need to modify the configuration file (named `topology.yaml`) according to the topology description and templates in the corresponding links. For other scenarios, edit the configuration template accordingly.

| Application | Configuration task | Configuration file template | Topology description |
| :-- | :-- | :-- | :-- |
| OLTP | [Deploy minimal topology](https://docs.pingcap.com/tidb/stable/minimal-deployment-topology) | [Simple minimal configuration template](https://github.com/pingcap/docs/blob/master/config-templates/simple-mini.yaml) <br/> [Full minimal configuration template](https://github.com/pingcap/docs/blob/master/config-templates/complex-mini.yaml) | This is the basic cluster topology, including tidb-server, tikv-server, and pd-server. |
| HTAP | [Deploy the TiFlash topology](https://docs.pingcap.com/tidb/stable/tiflash-deployment-topology) | [Simple TiFlash configuration template](https://github.com/pingcap/docs/blob/master/config-templates/simple-tiflash.yaml) <br/> [Full TiFlash configuration template](https://github.com/pingcap/docs/blob/master/config-templates/complex-tiflash.yaml) | This is to deploy TiFlash along with the minimal cluster topology. TiFlash is a columnar storage engine, and gradually becomes a standard cluster topology. |
| Replicate incremental data using [TiCDC](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-overview) | [Deploy the TiCDC topology](https://docs.pingcap.com/tidb/stable/ticdc-deployment-topology) | [Simple TiCDC configuration template](https://github.com/pingcap/docs/blob/master/config-templates/simple-cdc.yaml) <br/> [Full TiCDC configuration template](https://github.com/pingcap/docs/blob/master/config-templates/complex-cdc.yaml) | This is to deploy TiCDC along with the minimal cluster topology. TiCDC supports multiple downstream platforms, such as TiDB, MySQL, Kafka, MQ, and storage services. |
| Replicate incremental data using [TiDB Binlog](https://docs.pingcap.com/tidb/stable/tidb-binlog/tidb-binlog-overview) | [Deploy the TiDB Binlog topology](https://docs.pingcap.com/tidb/stable/tidb-binlog-deployment-topology) | [Simple TiDB Binlog configuration template (MySQL as downstream)](https://github.com/pingcap/docs/blob/master/config-templates/simple-tidb-binlog.yaml) <br/> [Simple TiDB Binlog configuration template (Files as downstream)](https://github.com/pingcap/docs/blob/master/config-templates/simple-file-binlog.yaml) <br/> [Full TiDB Binlog configuration template](https://github.com/pingcap/docs/blob/master/config-templates/complex-tidb-binlog.yaml) | This is to deploy TiDB Binlog along with the minimal cluster topology. |
| Use OLAP on Spark | [Deploy the TiSpark topology](https://docs.pingcap.com/tidb/stable/tispark-deployment-topology) | [Simple TiSpark configuration template](https://github.com/pingcap/docs/blob/master/config-templates/simple-tispark.yaml) <br/> [Full TiSpark configuration template](https://github.com/pingcap/docs/blob/master/config-templates/complex-tispark.yaml) |  This is to deploy TiSpark along with the minimal cluster topology. TiSpark is a component built for running Apache Spark on top of TiDB/TiKV to answer the OLAP queries. Currently, TiUP cluster's support for TiSpark is still **experimental**. |
| Deploy multiple instances on a single machine | [Deploy a hybrid topology](https://docs.pingcap.com/tidb/stable/hybrid-deployment-topology) | [Simple configuration template for hybrid deployment](https://github.com/pingcap/docs/blob/master/config-templates/simple-multi-instance.yaml) <br/> [Full configuration template for hybrid deployment](https://github.com/pingcap/docs/blob/master/config-templates/complex-multi-instance.yaml) | The deployment topologies also apply when you need to add extra configurations for the directory, port, resource ratio, and label. |
| Deploy TiDB clusters across data centers | [Deploy a geo-distributed deployment topology](https://docs.pingcap.com/tidb/stable/geo-distributed-deployment-topology) | [Configuration template for geo-distributed deployment](https://github.com/pingcap/docs/blob/master/config-templates/geo-redundancy-deployment.yaml) | This topology takes the typical architecture of three data centers in two cities as an example. It introduces the geo-distributed deployment architecture and the key configuration that requires attention. |

> **Note:**
>
> - For parameters that should be globally effective, configure these parameters of corresponding components in the `server_configs` section of the configuration file.
> - For parameters that should be effective on a specific node, configure these parameters in the `config` of this node.
> - Use `.` to indicate the subcategory of the configuration, such as `log.slow-threshold`. For more formats, see [TiUP configuration template](https://github.com/pingcap/tiup/blob/master/embed/examples/cluster/topology.example.yaml).
> - If you need to specify the user group name to be created on the target machine, see [this example](https://github.com/pingcap/tiup/blob/master/embed/examples/cluster/topology.example.yaml#L7).

For more configuration description, see the following configuration examples:

- [TiDB `config.toml.example`](https://github.com/pingcap/tidb/blob/release-8.1/pkg/config/config.toml.example)
- [TiKV `config.toml.example`](https://github.com/tikv/tikv/blob/release-8.1/etc/config-template.toml)
- [PD `config.toml.example`](https://github.com/pingcap/pd/blob/release-8.1/conf/config.toml)
- [TiFlash `config.toml.example`](https://github.com/pingcap/tiflash/blob/release-8.1/etc/config-template.toml)
