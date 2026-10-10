# Minimal TiDB deployment topology and templates

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/minimal-deployment-topology.md`
- Source Title: `Minimal Deployment Topology`
- Source Heading Path: `Minimal Deployment Topology | Minimal Deployment Topology > Topology information | Minimal Deployment Topology > Topology information > Topology templates`
- Source Line Ranges: `5-33`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `pd`, `tikv`, `tiup`
- Topic Tags: `deployment-topology`, `instance-layout`, `resource-sizing`, `ip-addresses`, `topology-templates`, `configuration-file`, `tiup`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0047_848c5725ed`
- Source ID: `tidb-docs-8.1:minimal-deployment-topology.md#minimal-deployment-topology`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5d83435c7134311bb6facd1373ce603f301bfd98f175d759950a947d980fe3e1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/minimal-deployment-topology#minimal-deployment-topology
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/minimal-deployment-topology.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the minimal self-managed TiDB cluster topology, including instance counts, example IP layout, machine sizing, and available TiUP topology templates.
- Retrieval Keywords: Minimal Deployment Topology, Topology information, Topology templates, simple-mini.yaml, complex-mini.yaml, Topology Configuration File for Deploying TiDB Using TiUP, TiUP cluster, TiDB 2 instances, PD 3 instances, TiKV 3 instances, Monitoring & Grafana 1 instance, 10.0.1.1, 10.0.1.10, global directory configuration, default port, relative path deployment directory, tidb user automatically creates
- Follow-up Guidance: The source also points to the topology reference for deploying TiDB using TiUP and notes that TiUP cluster automatically creates the `tidb` user and that a relative deployment directory is placed in the user's home directory.
- Classification Note: This is classified as architecture because the content defines the minimal deployment topology, instance layout, resource sizing, example IP addresses, and topology file templates for a TiDB cluster.

## Official Source Content

# Minimal Deployment Topology

This document describes the minimal deployment topology of TiDB clusters.
## Topology information

| Instance | Count | Physical machine configuration | IP | Configuration |
| :-- | :-- | :-- | :-- | :-- |
| TiDB | 2 | 16 VCore 32 GiB <br/> 100 GiB for storage | 10.0.1.1 <br/> 10.0.1.2 | Default port <br/> Global directory configuration |
| PD | 3 | 4 VCore 8 GiB <br/> 100 GiB for storage |10.0.1.4 <br/> 10.0.1.5 <br/> 10.0.1.6 | Default port <br/> Global directory configuration |
| TiKV | 3 | 16 VCore 32 GiB <br/> 2 TiB (NVMe SSD) for storage | 10.0.1.7 <br/> 10.0.1.8 <br/> 10.0.1.9 | Default port <br/> Global directory configuration |
| Monitoring & Grafana | 1 | 4 VCore 8 GiB <br/> 500 GiB (SSD) for storage | 10.0.1.10 | Default port <br/> Global directory configuration |

> **Note:**
>
> The IP addresses of the instances are given as examples only. In your actual deployment, replace the IP addresses with your actual IP addresses.
### Topology templates

- [The simple template for the minimal topology](https://github.com/pingcap/docs/blob/master/config-templates/simple-mini.yaml)
- [The complex template for the minimal topology](https://github.com/pingcap/docs/blob/master/config-templates/complex-mini.yaml)

For detailed descriptions of the configuration items in the above TiDB cluster topology file, see [Topology Configuration File for Deploying TiDB Using TiUP](https://docs.pingcap.com/tidb/stable/tiup/tiup-cluster-topology-reference).

> **Note:**
>
> - You do not need to manually create the `tidb` user in the configuration file. The TiUP cluster component automatically creates the `tidb` user on the target machines. You can customize the user, or keep the user consistent with the control machine.
> - If you configure the deployment directory as a relative path, the cluster will be deployed in the home directory of the user.
