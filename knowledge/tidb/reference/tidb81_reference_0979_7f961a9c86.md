# TiUP topology reference for alertmanager_servers

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-cluster-topology-reference.md`
- Source Title: `Topology Configuration File for TiDB Deployment Using TiUP`
- Source Heading Path: `Topology Configuration File for TiDB Deployment Using TiUP > File structure > `alertmanager_servers``
- Source Line Ranges: `893-942`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `shared`
- Topic Tags: `topology-file`, `alertmanager`, `server-configuration`, `ports`, `deploy-dir`, `data-dir`, `log-dir`, `resource-control`, `numa`, `listen-host`, `immutable-fields`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0979_7f961a9c86`
- Source ID: `tidb-docs-8.1:tiup/tiup-cluster-topology-reference.md#alertmanager-servers`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b1e81ebc4ef447d3cfc6b1411a89340421e86968eb8bbfe4908a1afacfe8fac3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-cluster-topology-reference#alertmanager-servers
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-cluster-topology-reference.md

## Retrieval Guidance

- Use When: Use this chunk when looking up the topology file fields for `alertmanager_servers` in TiUP, including ports, directories, host settings, resource control, and immutable fields after deployment.
- Retrieval Keywords: alertmanager_servers, TiUP topology reference, host, ssh_port, web_port, 9093, cluster_port, 9094, deploy_dir, data_dir, log_dir, numa_node, numactl, config_file, os, arch, resource_control, listen_host, 0.0.0.0, immutable fields, cannot modify after deployment
- Follow-up Guidance: The source also includes an `alertmanager_servers` YAML example with `host` and `config_file` entries.
- Classification Note: This is reference content because it enumerates the supported `alertmanager_servers` topology fields, default behaviors, merge behavior, and the fields that cannot be modified after deployment.

## Official Source Content

### `alertmanager_servers`

`alertmanager_servers` specifies the machines to which the Alertmanager services are deployed. It also specifies the service configuration on each machine. `alertmanager_servers` is an array. Each array element contains the following fields:

- `host`: Specifies the machine to which the Alertmanager services are deployed. The field value is an IP address and is mandatory.

- `ssh_port`: Specifies the SSH port to connect to the target machine for operations. If it is not specified, the `ssh_port` of the `global` section is used.

- `web_port`: Specifies the port used that Alertmanager uses to provide web services. The default value is `9093`.

- `cluster_port`: Specifies the communication port between one Alertmanger and other Alertmanager. The default value is `9094`.

- `deploy_dir`: Specifies the deployment directory. If it is not specified or specified as a relative directory, the directory is generated according to the `deploy_dir` directory configured in `global`.

- `data_dir`: Specifies the data directory. If it is not specified or specified as a relative directory, the directory is generated according to the `data_dir` directory configured in `global`.

- `log_dir`: Specifies the log directory. If it is not specified or specified as a relative directory, the log is generated according to the `log_dir` directory configured in `global`.

- `numa_node`: Allocates the NUMA policy to the instance. Before specifying this field, you need to make sure that the target machine has [numactl](https://linux.die.net/man/8/numactl) installed. If this field is specified, cpubind and membind policies are allocated using [numactl](https://linux.die.net/man/8/numactl). This field is the string type. The field value is the ID of the NUMA node, such as "0,1".

- `config_file`: Specifies a local file that is transferred to the target machine during the initialization phase of the cluster configuration as the configuration of Alertmanager.

- `os`: The operating system of the machine specified in `host`. If this field is not specified, the default value is the `os` value in `global`.

- `arch`: The architecture of the machine specified in `host`. If this field is not specified, the default value is the `arch` value in `global`.

- `resource_control`: Resource control for the service. If this field is configured, the field content is merged with the `resource_control` content in `global` (if the two fields overlap, the content of this field takes effect). Then, a systemd configuration file is generated and sent to the machine specified in `host`. The configuration rules of `resource_control` are the same as the `resource_control` content in `global`.

- `listen_host`: Specifies the listening address so that Alertmanager can be accessed through a proxy. It is recommended to configure it as `0.0.0.0`. For more information, see [Customize Alertmanager configurations](https://docs.pingcap.com/tidb/stable/tiup/customized-montior-in-tiup-environment#customize-alertmanager-configurations).

For the above fields, you cannot modify these configured fields after the deployment:

- `host`
- `web_port`
- `cluster_port`
- `deploy_dir`
- `data_dir`
- `log_dir`
- `arch`
- `os`

A `alertmanager_servers` configuration example is as follows:

```yaml
alertmanager_servers:
  - host: 10.0.1.11
    config_file: /local/config/file
  - host: 10.0.1.12
    config_file: /local/config/file
```
