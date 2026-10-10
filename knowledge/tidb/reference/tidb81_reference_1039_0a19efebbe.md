# DM TiUP alertmanager_servers topology fields and example

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-dm-topology-reference.md`
- Source Title: `Topology Configuration File for DM Cluster Deployment Using TiUP`
- Source Heading Path: `Topology Configuration File for DM Cluster Deployment Using TiUP > `worker_servers` > `alertmanager_servers``
- Source Line Ranges: `277-313`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `dm`, `shared`
- Topic Tags: `topology-file`, `alertmanager`, `deployment`, `configuration-fields`, `ports`, `directories`, `numa`, `resource-control`, `immutable-fields`, `yaml-example`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_1039_0a19efebbe`
- Source ID: `tidb-docs-8.1:tiup/tiup-dm-topology-reference.md#alertmanager-servers`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `61ba290f28d7bd063a7a363185f744fba963274e5811aa71457c6582ccb3a913`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-dm-topology-reference#alertmanager-servers
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-dm-topology-reference.md

## Retrieval Guidance

- Use When: Use this chunk when looking up the `alertmanager_servers` section of a DM TiUP topology file, including its fields, defaults, immutable items, and YAML example.
- Retrieval Keywords: alertmanager_servers, DM TiUP topology, Topology Configuration File for DM Cluster Deployment Using TiUP, host, ssh_port, web_port, cluster_port, deploy_dir, data_dir, log_dir, numa_node, config_file, os, arch, resource_control, immutable fields, Alertmanager YAML example
- Follow-up Guidance: The chunk also states that `host`, `web_port`, `cluster_port`, `deploy_dir`, `data_dir`, `log_dir`, `arch`, and `os` cannot be modified after deployment is completed.
- Classification Note: This is reference content because it enumerates the `alertmanager_servers` topology fields, their meanings and defaults, immutability constraints, and a configuration example from the official documentation.

## Official Source Content

### `alertmanager_servers`

`alertmanager_servers` specifies the machines to which the Alertmanager service is deployed. You can also specify the service configuration on each machine. `alertmanager_servers` is an array. Each array element contains the following fields:

- `host`: specifies the machine to deploy to. The field value is an IP address and is mandatory.
- `ssh_port`: specifies the SSH port to connect to the target machine for operations. If the field is not specified, the `ssh_port` in the `global` section is used.
- `web_port`: specify the port on which Alertmanager provides web services. The default value is "9093".
- `cluster_port`: Specify the communication port between one Alertmanger and other Alertmanager. The default value is "9094".
- `deploy_dir`: specifies the deployment directory. If the field is not specified, or specified as a relative directory, the deployment directory is generated according to the `deploy_dir` configuration in the `global` section.
- `data_dir`: specifies the data directory. If the field is not specified, or specified as a relative directory, the data directory is generated according to the `data_dir` configuration in the `global` section.
- `log_dir`: specifies the log directory. If the field is not specified, or specified as a relative directory, the log directory is generated according to the `log_dir` configuration in the `global` section.
- `numa_node`: allocates the NUMA policy to the instance. Before specifying this field, you need to make sure that the target machine has [numactl](https://linux.die.net/man/8/numactl) installed. If this field is specified, cpubind and membind policies are allocated using [numactl](https://linux.die.net/man/8/numactl). This field is a string type. The field value is the ID of the NUMA node, such as "0,1"
- `config_file`: specifies a local file. The specified file will be sent to the target machine as the configuration for Alertmanager during the initialization phase of the cluster configuration.
- `os`: the operating system of the machine specified in the `host` field. If the field is not specified, the default value is the `os` value configured in the `global` section.
- `arch`: the architecture of the machine specified in the `host` field. If the field is not specified, the default value is the `arch` value configured in the `global` section.
- `resource_control`: resource control on this service. If this field is specified, the configuration of this field will be merged with the configuration of `resource_control` in the `global` section (if the two fields overlap, the configuration of this field takes effect), and then the configuration file of systemd is generated and distributed to the machine specified in the `host` field. The configuration rules of this field are the same as that of `resource_control` in the `global` section.

In `alertmanager_servers`, the following fields cannot be modified after the deployment is completed:

- `host`
- `web_port`
- `cluster_port`
- `deploy_dir`
- `data_dir`
- `log_dir`
- `arch`
- `os`

An `alertmanager_servers` configuration example is as follows:

```yaml
alertmanager_servers:
  - host: 10.0.1.11
    config_file: /local/config/file
  - host: 10.0.1.12
    config_file: /local/config/file
```
