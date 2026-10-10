# TiFlash deployment topology, templates, and key parameters

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiflash-deployment-topology.md`
- Source Title: `TiFlash Deployment Topology`
- Source Heading Path: `TiFlash Deployment Topology | TiFlash Deployment Topology > Topology information | TiFlash Deployment Topology > Topology information > Topology templates | TiFlash Deployment Topology > Topology information > Key parameters`
- Source Line Ranges: `5-42`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `tidb`, `tikv`, `pd`, `tiup`, `shared`
- Topic Tags: `deployment-topology`, `topology-template`, `configuration-parameters`, `placement-rules`, `instance-host`, `global-directory`, `tidb-user`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0948_676c9b3ad1`
- Source ID: `tidb-docs-8.1:tiflash-deployment-topology.md#tiflash-deployment-topology`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b7cb516fac9c9ced92dc976ee9c0a6acd33a21af410cbe7ff66a811304e07d37`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiflash-deployment-topology#tiflash-deployment-topology
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiflash-deployment-topology.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the self-managed TiFlash deployment topology, topology templates, and key parameters in a minimal TiDB topology.
- Retrieval Keywords: TiFlash Deployment Topology, simple-tiflash.yaml, complex-tiflash.yaml, Topology Configuration File for Deploying TiDB Using TiUP, replication.enable-placement-rules, Placement Rules, tiflash_servers, -host, only supports IP, not domain name, Global directory configuration, tidb user, deployment directory as a relative path
- Follow-up Guidance: The source also points to TiFlash Configuration and the TiUP cluster topology reference for detailed parameter descriptions.
- Classification Note: This is reference content because it lists the TiFlash topology layout, template files, component machine specifications, and exact configuration parameters and notes from the official deployment documentation.

## Official Source Content

# TiFlash Deployment Topology

This document describes the deployment topology of [TiFlash](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-overview) based on the minimal TiDB topology.

TiFlash is a columnar storage engine, and gradually becomes the standard cluster topology. It is suitable for real-time HTAP applications.
## Topology information

| Instance | Count | Physical machine configuration | IP | Configuration |
| :-- | :-- | :-- | :-- | :-- |
| TiDB | 3 | 16 VCore 32GB * 1 | 10.0.1.7 <br/> 10.0.1.8 <br/> 10.0.1.9 | Default port <br/> Global directory configuration |
| PD | 3 | 4 VCore 8GB * 1 | 10.0.1.4 <br/> 10.0.1.5 <br/> 10.0.1.6 | Default port <br/> Global directory configuration |
| TiKV | 3 | 16 VCore 32GB 2TB (nvme ssd) * 1 | 10.0.1.1 <br/> 10.0.1.2 <br/> 10.0.1.3 | Default port <br/> Global directory configuration |
| TiFlash | 1 | 32 VCore 64 GB 2TB (nvme ssd) * 1  | 10.0.1.11 | Default port <br/> Global directory configuration |
| Monitoring & Grafana | 1 | 4 VCore 8GB * 1 500GB (ssd) | 10.0.1.10 | Default port <br/> Global directory configuration |

> **Note:**
>
> The IP addresses of the instances are given as examples only. In your actual deployment, replace the IP addresses with your actual IP addresses.
### Topology templates

- [The simple template for the TiFlash topology](https://github.com/pingcap/docs/blob/master/config-templates/simple-tiflash.yaml)
- [The complex template for the TiFlash topology](https://github.com/pingcap/docs/blob/master/config-templates/complex-tiflash.yaml)

For detailed descriptions of the configuration items in the above TiDB cluster topology file, see [Topology Configuration File for Deploying TiDB Using TiUP](https://docs.pingcap.com/tidb/stable/tiup/tiup-cluster-topology-reference).
### Key parameters

- To enable the [Placement Rules](https://docs.pingcap.com/tidb/stable/configure-placement-rules) feature of PD, set the value of `replication.enable-placement-rules` in the configuration template to `true`.
- The instance level `"-host"` configuration in `tiflash_servers` only supports IP, not domain name.
- For detailed TiFlash parameter description, see [TiFlash Configuration](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-configuration).

> **Note:**
>
> - You do not need to manually create the `tidb` user in the configuration file. The TiUP cluster component automatically creates the `tidb` user on the target machines. You can customize the user, or keep the user consistent with the control machine.
> - If you configure the deployment directory as a relative path, the cluster will be deployed in the home directory of the user.
