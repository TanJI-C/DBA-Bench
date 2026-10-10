# Deploy primary and secondary clusters with TiCDC topology

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dr-secondary-cluster.md`
- Source Title: `DR Solution Based on Primary and Secondary Clusters`
- Source Heading Path: `DR Solution Based on Primary and Secondary Clusters > Set up primary and secondary clusters based on TiCDC > Set up primary and secondary clusters`
- Source Line Ranges: `43-105`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `ticdc`, `tidb`, `tikv`, `pd`
- Topic Tags: `deployment`, `topology`, `regional-placement`, `cluster-setup`, `ticdc-deployment`, `yaml`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0095_8c8d4b2ea8`
- Source ID: `tidb-docs-8.1:dr-secondary-cluster.md#set-up-primary-and-secondary-clusters`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `095721c15114f17ece82070555620376b1e080d75f054c9a35b30db13bd1371c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dr-secondary-cluster#set-up-primary-and-secondary-clusters
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dr-secondary-cluster.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the deployment topology and TiUP YAML template for primary and secondary TiDB clusters with TiCDC deployed together with the secondary cluster.
- Retrieval Keywords: Set up primary and secondary clusters, deployment topology, TiUP, yaml, cdc_servers, gc-ttl, ticdc_cluster_id, DR_TiCDC, region 1, region 2, PD, TiDB, TiKV, Monitor, Grafana, AlertManager, Deploy a TiDB cluster, Deploy TiCDC, secondary cluster and TiCDC must be deployed and managed together
- Follow-up Guidance: The source points to Deploy a TiDB cluster for deployment details and Deploy TiCDC for adding or scaling out TiCDC to an existing TiDB cluster.
- Classification Note: This chunk is classified as configuration because it provides node placement, component topology, and a concrete deployment template with configuration fields such as cdc_servers, gc-ttl, data_dir, and ticdc_cluster_id.

## Official Source Content

### Set up primary and secondary clusters

In this document, the TiDB primary and secondary clusters are deployed in two different regions (region 1 and region 2). TiCDC is deployed together with the secondary cluster, because there is a certain network latency between the primary and secondary clusters. Deploying TiCDC with the secondary cluster can avoid the impact of network latency, which helps achieve optimal replication performance. The deployment topology of the example provided in this document is as follows (one component node is deployed on one server):

|Region | Host | Cluster | Component |
| --- | --- | --- | --- |
| Region 1 | 10.0.1.9 | Primary | Monitor, Grafana, or AlterManager |
| Region 2 | 10.0.1.11 | Secondary | Monitor, Grafana, or AlterManager |
| Region 1 | 10.0.1.1/10.0.1.2/10.0.1.3 | Primary | PD |
| Region 2 | 10.1.1.1/10.1.1.2/10.1.1.3 | Secondary | PD |
| Region 2 | 10.1.1.9/10.1.1.10 | Primary | TiCDC |
| Region 1 | 10.0.1.4/10.0.1.5 | Primary| TiDB |
| Region 2 | 10.1.1.4/10.1.1.5 | Secondary | TiDB |
| Region 1 | 10.0.1.6/10.0.1.7/10.0.1.8 | Primary | TiKV |
| Region 2 | 10.1.1.6/10.1.1.7/10.1.1.8 | Secondary | TiKV |

For server configurations, see the following documents:

- [Software and hardware recommendations for TiDB](https://docs.pingcap.com/tidb/stable/hardware-and-software-requirements)
- [Software and hardware recommendations for TiCDC](https://docs.pingcap.com/tidb/stable/ticdc/deploy-ticdc#software-and-hardware-recommendations)

For details about how to deploy TiDB primary and secondary clusters, see [Deploy a TiDB cluster](https://docs.pingcap.com/tidb/stable/production-deployment-using-tiup).

When deploying TiCDC, note that the secondary cluster and TiCDC must be deployed and managed together, and the network between them must be connected.

- To deploy TiCDC on an existing primary cluster, see [Deploy TiCDC](https://docs.pingcap.com/tidb/stable/ticdc/deploy-ticdc#add-or-scale-out-ticdc-to-an-existing-tidb-cluster-using-tiup).
- To deploy a new primary cluster and TiCDC, use the following deployment template and modify the configuration parameters as needed:

    ```yaml
    global:
    user: "tidb"
    ssh_port: 22
    deploy_dir: "/tidb-deploy"
    data_dir: "/tidb-data"
    server_configs: {}
    pd_servers:
    - host: 10.0.1.1
    - host: 10.0.1.2
    - host: 10.0.1.3
    tidb_servers:
    - host: 10.0.1.4
    - host: 10.0.1.5
    tikv_servers:
    - host: 10.0.1.6
    - host: 10.0.1.7
    - host: 10.0.1.8
    monitoring_servers:
    - host: 10.0.1.9
    grafana_servers:
    - host: 10.0.1.9
    alertmanager_servers:
    - host: 10.0.1.9
    cdc_servers:
    - host: 10.1.1.9
        gc-ttl: 86400
        data_dir: "/cdc-data"
        ticdc_cluster_id: "DR_TiCDC"
    - host: 10.1.1.10
        gc-ttl: 86400
        data_dir: "/cdc-data"
        ticdc_cluster_id: "DR_TiCDC"
    ```
