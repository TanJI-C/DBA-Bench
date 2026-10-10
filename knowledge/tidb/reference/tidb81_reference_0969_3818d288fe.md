# TiUP topology file overview and section map

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-cluster-topology-reference.md`
- Source Title: `Topology Configuration File for TiDB Deployment Using TiUP`
- Source Heading Path: `Topology Configuration File for TiDB Deployment Using TiUP | Topology Configuration File for TiDB Deployment Using TiUP > File structure`
- Source Line Ranges: `5-36`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `pd`, `tidb`, `tikv`, `tiflash`, `tiproxy`, `ticdc`, `shared`
- Topic Tags: `topology-file`, `deployment`, `scale-out`, `monitoring`, `component-sections`, `versions`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0969_3818d288fe`
- Source ID: `tidb-docs-8.1:tiup/tiup-cluster-topology-reference.md#topology-configuration-file-for-tidb-deployment-using-tiup`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `19eeda6ebe9533df68cb2661d0a5e0adf9781e75bcf7e21c608f59499da1f080`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-cluster-topology-reference#topology-configuration-file-for-tidb-deployment-using-tiup
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-cluster-topology-reference.md

## Retrieval Guidance

- Use When: Use this chunk when you need the section map of a TiUP topology file for TiDB deployment, scale out, or topology modification and want the exact section names available in the file structure.
- Retrieval Keywords: topology configuration file, TiUP topology file, File structure, global, monitored, server_configs, component_versions, pd_servers, tidb_servers, tikv_servers, tiflash_servers, tiproxy_servers, pump_servers, drainer_servers, kvcdc_servers, cdc_servers, tispark_masters, tispark_workers, monitoring_servers, grafana_servers, alertmanager_servers, deploy or scale TiDB using TiUP
- Follow-up Guidance: The content also points to Customize Configurations of Monitoring Servers for Prometheus, Grafana, and Alertmanager customization in a TiUP environment.
- Classification Note: This is reference content because it enumerates the topology file sections and briefly states what each section configures.

## Official Source Content

# Topology Configuration File for TiDB Deployment Using TiUP

To deploy or scale TiDB using TiUP, you need to provide a topology file ([sample](https://github.com/pingcap/tiup/blob/master/embed/examples/cluster/topology.example.yaml)) to describe the cluster topology.

Similarly, to modify the cluster topology, you need to modify the topology file. The difference is that, after the cluster is deployed, you can only modify a part of the fields in the topology file. This document introduces each section of the topology file and each field in each section.

When you deploy a TiDB cluster using TiUP, TiUP also deploys monitoring servers, such as Prometheus, Grafana, and Alertmanager. In the meantime, if you scale out this cluster, TiUP also adds the new nodes into monitoring scope. To customize the configurations of the preceding monitoring servers, you can follow the instructions in [Customize Configurations of Monitoring Servers](https://docs.pingcap.com/tidb/stable/tiup/customized-montior-in-tiup-environment).
## File structure

A topology configuration file for TiDB deployment using TiUP might contain the following sections:

- [global](#global): The cluster's global configuration. Some of the configuration items use the default values and you can configure them separately in each instance.
- [monitored](#monitored): Configuration for monitoring services, namely, the blackbox_exporter and the `node_exporter`. On each machine, a `node_exporter` and a `blackbox_exporter` are deployed.
- [server_configs](#server_configs): Components' global configuration. You can configure each component separately. If an instance has a configuration item with the same name, the instance's configuration item will take effect.
- [component_versions](#component_versions): Component version. You can configure it when a component does not use the cluster version. This section is introduced in tiup-cluster v1.14.0.
- [pd_servers](#pd_servers): The configuration of the PD instance. This configuration specifies the machines to which the PD component is deployed.
- [tidb_servers](#tidb_servers): The configuration of the TiDB instance. This configuration specifies the machines to which the TiDB component is deployed.
- [tikv_servers](#tikv_servers): The configuration of the TiKV instance. This configuration specifies the machines to which the TiKV component is deployed.
- [tiflash_servers](#tiflash_servers): The configuration of the TiFlash instance. This configuration specifies the machines to which the TiFlash component is deployed.
- [tiproxy_servers](#tiproxy_servers): The configuration of the TiProxy instance. This configuration specifies the machines to which the TiProxy component is deployed.
- [pump_servers](#pump_servers): The configuration of the Pump instance. This configuration specifies the machines to which the Pump component is deployed.
- [drainer_servers](#drainer_servers): The configuration of the Drainer instance. This configuration specifies the machines to which the Drainer component is deployed.
- [kvcdc_servers](#kvcdc_servers): The configuration of the [TiKV-CDC](https://tikv.org/docs/7.1/concepts/explore-tikv-features/cdc/cdc/) instance. This configuration specifies the machines to which the TiKV-CDC component is deployed.
- [cdc_servers](#cdc_servers): The configuration of the TiCDC instance. This configuration specifies the machines to which the TiCDC component is deployed.
- [tispark_masters](#tispark_masters): The configuration of the TiSpark master instance. This configuration specifies the machines to which the TiSpark master component is deployed. Only one node of TiSpark master can be deployed.
- [tispark_workers](#tispark_workers): The configuration of the TiSpark worker instance. This configuration specifies the machines to which the TiSpark worker component is deployed.
- [monitoring_servers](#monitoring_servers): Specifies the machines to which Prometheus and NGMonitoring are deployed. TiUP supports deploying multiple Prometheus instances but only the first instance is used.
- [grafana_servers](#grafana_servers): The configuration of the Grafana instance. This configuration specifies the machines to which Grafana is deployed.
- [alertmanager_servers](#alertmanager_servers): The configuration of the Alertmanager instance. This configuration specifies the machines to which Alertmanager is deployed.
