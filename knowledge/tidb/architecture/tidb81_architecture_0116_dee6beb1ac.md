# TiSpark deployment topology, templates, and prerequisites

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tispark-deployment-topology.md`
- Source Title: `TiSpark Deployment Topology`
- Source Heading Path: `TiSpark Deployment Topology | TiSpark Deployment Topology > Topology information | TiSpark Deployment Topology > Topology templates | TiSpark Deployment Topology > Prerequisites`
- Source Line Ranges: `6-51`
- Source Scope: `self_managed`
- Primary Component: `ecosystem`
- Related Components: `tidb`, `tikv`, `pd`, `tiup`, `shared`
- Topic Tags: `deployment-topology`, `deprecated-support`, `cluster-layout`, `topology-template`, `prerequisites`, `jre`, `java-home`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0116_dee6beb1ac`
- Source ID: `tidb-docs-8.1:tispark-deployment-topology.md#tispark-deployment-topology`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c3d22dcd453422e0ef4c9d102496e7f8eefbf92d3be532ce01df772f3e90808e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tispark-deployment-topology#tispark-deployment-topology
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tispark-deployment-topology.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks about TiSpark deployment topology in TiUP, available topology templates, or prerequisites such as JRE 8 and the `java_home` setting.
- Retrieval Keywords: TiSpark Deployment Topology, TiSpark support in the TiUP cluster is deprecated, minimum cluster topology, Simple TiSpark topology template, Complex TiSpark topology template, Topology Configuration File for Deploying TiDB Using TiUP, JRE 8, Java Runtime Environment (JRE) 8, java_home, JAVA_HOME, TiUP does not support installing JRE automatically, tidb user automatically creates, relative path deployment directory
- Follow-up Guidance: For more information about the TiSpark architecture and how to use it, see TiSpark User Guide, and for detailed descriptions of topology configuration items, see Topology Configuration File for Deploying TiDB Using TiUP.
- Classification Note: This chunk is classified as architecture because it describes the TiSpark cluster layout, topology templates, component placement, and deployment prerequisites in a self-managed TiDB ecosystem context.

## Official Source Content

# TiSpark Deployment Topology

> **Warning:**
>
> TiSpark support in the TiUP cluster is deprecated. It is **NOT** recommended to use it.

This document introduces the TiSpark deployment topology and how to deploy TiSpark based on the minimum cluster topology.

TiSpark is a component built for running Apache Spark on top of TiDB/TiKV to answer complex OLAP queries. It brings benefits of both the Spark platform and the distributed TiKV cluster to TiDB and makes TiDB a one-stop solution for both online transactions and analytics.

For more information about the TiSpark architecture and how to use it, see [TiSpark User Guide](https://docs.pingcap.com/tidb/stable/tispark-overview).
## Topology information

| Instance | Count | Physical machine configuration | IP | Configuration |
| :-- | :-- | :-- | :-- | :-- |
| TiDB | 3 | 16 VCore 32GB * 1 | 10.0.1.1 <br/> 10.0.1.2 <br/> 10.0.1.3 | Default port <br/>  Global directory configuration |
| PD | 3 | 4 VCore 8GB * 1 |10.0.1.4 <br/> 10.0.1.5 <br/> 10.0.1.6 | Default port <br/> Global directory configuration |
| TiKV | 3 | 16 VCore 32GB 2TB (nvme ssd) * 1 | 10.0.1.7 <br/> 10.0.1.8 <br/> 10.0.1.9 | Default port <br/> Global directory configuration |
| TiSpark | 3 | 8 VCore 16GB * 1 | 10.0.1.21 (master) <br/> 10.0.1.22 (worker) <br/> 10.0.1.23 (worker) | Default port <br/> Global directory configuration |
| Monitoring & Grafana | 1 | 4 VCore 8GB * 1 500GB (ssd) | 10.0.1.11 | Default port <br/> Global directory configuration |

> **Note:**
>
> The IP addresses of the instances are given as examples only. In your actual deployment, replace the IP addresses with your actual IP addresses.
## Topology templates

- [Simple TiSpark topology template](https://github.com/pingcap/docs/blob/master/config-templates/simple-tispark.yaml)
- [Complex TiSpark topology template](https://github.com/pingcap/docs/blob/master/config-templates/complex-tispark.yaml)

For detailed descriptions of the configuration items in the above TiDB cluster topology file, see [Topology Configuration File for Deploying TiDB Using TiUP](https://docs.pingcap.com/tidb/stable/tiup/tiup-cluster-topology-reference).

> **Note:**
>
> - You do not need to manually create the `tidb` user in the configuration file. The TiUP cluster component automatically creates the `tidb` user on the target machines. You can customize the user, or keep the user consistent with the control machine.
> - If you configure the deployment directory as a relative path, the cluster will be deployed in the home directory of the user.
## Prerequisites

TiSpark is based on the Apache Spark cluster, so before you start the TiDB cluster that contains TiSpark, you must ensure that Java Runtime Environment (JRE) 8 is installed on the server that deploys TiSpark. Otherwise, TiSpark cannot be started.

TiUP does not support installing JRE automatically. You need to install it on your own. For detailed installation instruction, see [How to download and install prebuilt OpenJDK packages](https://openjdk.java.net/install/).

If JRE 8 has already been installed on the deployment server but is not in the path of the system's default package management tool, you can specify the path of the JRE environment to be used by setting the `java_home` parameter in the topology configuration. This parameter corresponds to the `JAVA_HOME` system environment variable.
