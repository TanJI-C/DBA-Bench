# TiUP topology PD and TiDB server instance definitions

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-cluster-topology-reference.md`
- Source Title: `Topology Configuration File for TiDB Deployment Using TiUP`
- Source Heading Path: `Topology Configuration File for TiDB Deployment Using TiUP > File structure > `pd_servers` | Topology Configuration File for TiDB Deployment Using TiUP > File structure > `tidb_servers``
- Source Line Ranges: `205-312`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `pd`, `tidb`, `shared`
- Topic Tags: `topology-file`, `instance-fields`, `pd-servers`, `tidb-servers`, `immutable-fields`, `resource-control`, `numa`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0970_af02356638`
- Source ID: `tidb-docs-8.1:tiup/tiup-cluster-topology-reference.md#pd-servers`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `014ac74ce9e9cbf92129c81284f92dcc8f3691f351b5941a7fe5a7d55be61e09`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-cluster-topology-reference#pd-servers
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-cluster-topology-reference.md

## Retrieval Guidance

- Use When: Use this chunk when identifying the fields, defaults, merge behavior, and immutable settings for `pd_servers` and `tidb_servers` entries in a TiUP topology file.
- Retrieval Keywords: pd_servers, tidb_servers, host, listen_host, ssh_port, name, client_port, peer_port, port, status_port, deploy_dir, data_dir, log_dir, numa_node, numactl, config, resource_control, os, arch, cannot modify after deployment, instance definition
- Follow-up Guidance: The content states that instance-level `config` and `resource_control` are merged with the corresponding `server_configs` or `global` content, and overlapping instance fields take effect.
- Classification Note: This is classified as reference because the content enumerates per-instance topology fields, default values, and which fields cannot be modified after deployment.

## Official Source Content

### `pd_servers`

`pd_servers` specifies the machines to which PD services are deployed. It also specifies the service configuration on each machine. `pd_servers` is an array, and each element of the array contains the following fields:

- `host`: Specifies the machine to which the PD services are deployed. The field value is an IP address and is mandatory.

- `listen_host`: When the machine has multiple IP addresses, `listen_host` specifies the listening IP address of the service. The default value is `0.0.0.0`.

- `ssh_port`: Specifies the SSH port to connect to the target machine for operations. If it is not specified, the `ssh_port` of the `global` section is used.

- `name`: Specifies the name of the PD instance. Different instances must have unique names; otherwise, instances cannot be deployed.

- `client_port`: Specifies the port that PD uses to connect to the client. The default value is `2379`.

- `peer_port`: Specifies the port for communication between PDs. The default value is `2380`.

- `deploy_dir`: Specifies the deployment directory. If it is not specified or specified as a relative directory, the directory is generated according to the `deploy_dir` directory configured in `global`.

- `data_dir`: Specifies the data directory. If it is not specified or specified as a relative directory, the directory is generated according to the `data_dir` directory configured in `global`.

- `log_dir`: Specifies the log directory. If it is not specified or specified as a relative directory, the log is generated according to the `log_dir` directory configured in `global`.

- `numa_node`: Allocates the NUMA policy to the instance. Before specifying this field, you need to make sure that the target machine has [numactl](https://linux.die.net/man/8/numactl) installed. If this field is specified, cpubind and membind policies are allocated using [numactl](https://linux.die.net/man/8/numactl). This field is the string type. The field value is the ID of the NUMA node, such as "0,1".

- `config`: The configuration rule of this field is the same as the `pd` configuration rule in `server_configs`. If this field is configured, the field content is merged with the `pd` content in `server_configs` (if the two fields overlap, the content of this field takes effect). Then, a configuration file is generated and sent to the machine specified in `host`.

- `os`: The operating system of the machine specified in `host`. If this field is not specified, the default value is the `os` value in `global`.

- `arch`: The architecture of the machine specified in `host`. If this field is not specified, the default value is the `arch` value in `global`.

- `resource_control`: Resource control for the service. If this field is configured, the field content is merged with the `resource_control` content in `global` (if the two fields overlap, the content of this field takes effect). Then, a systemd configuration file is generated and sent to the machine specified in `host`. The configuration rules of `resource_control` are the same as the `resource_control` content in `global`.

For the above fields, you cannot modify these configured fields after the deployment:

- `host`
- `listen_host`
- `name`
- `client_port`
- `peer_port`
- `deploy_dir`
- `data_dir`
- `log_dir`
- `arch`
- `os`

A `pd_servers` configuration example is as follows:

```yaml
pd_servers:
  - host: 10.0.1.11
    config:
      schedule.max-merge-region-size: 20
      schedule.max-merge-region-keys: 200000
  - host: 10.0.1.12
```

The above configuration specifies that PD will be deployed on `10.0.1.11` and `10.0.1.12`, and makes specific configurations for the PD of `10.0.1.11`.
### `tidb_servers`

`tidb_servers` specifies the machines to which TiDB services are deployed. It also specifies the service configuration on each machine. `tidb_servers` is an array, and each element of the array contains the following fields:

- `host`: Specifies the machine to which the TiDB services are deployed. The field value is an IP address and is mandatory.

- `listen_host`: When the machine has multiple IP addresses, `listen_host` specifies the listening IP address of the service. The default value is `0.0.0.0`.

- `ssh_port`: Specifies the SSH port to connect to the target machine for operations. If it is not specified, the `ssh_port` of the `global` section is used.

- `port`: The listening port of TiDB services, which is used to provide connection to the MySQL client. The default value is `4000`.

- `status_port`: The listening port of the TiDB status service, which is used to view the status of the TiDB services from the external via HTTP requests. The default value is `10080`.

- `deploy_dir`: Specifies the deployment directory. If it is not specified or specified as a relative directory, the directory is generated according to the `deploy_dir` directory configured in `global`.

- `log_dir`: Specifies the log directory. If it is not specified or specified as a relative directory, the log is generated according to the `log_dir` directory configured in `global`.

- `numa_node`: Allocates the NUMA policy to the instance. Before specifying this field, you need to make sure that the target machine has [numactl](https://linux.die.net/man/8/numactl) installed. If this field is specified, cpubind and membind policies are allocated using [numactl](https://linux.die.net/man/8/numactl). This field is the string type. The field value is the ID of the NUMA node, such as "0,1".

- `config`: The configuration rule of this field is the same as the `tidb` configuration rule in `server_configs`. If this field is configured, the field content is merged with the `tidb` content in `server_configs` (if the two fields overlap, the content of this field takes effect). Then, a configuration file is generated and sent to the machine specified in `host`.

- `os`: The operating system of the machine specified in `host`. If this field is not specified, the default value is the `os` value in `global`.

- `arch`: The architecture of the machine specified in `host`. If this field is not specified, the default value is the `arch` value in `global`.

- `resource_control`: Resource control for the service. If this field is configured, the field content is merged with the `resource_control` content in `global` (if the two fields overlap, the content of this field takes effect). Then, a systemd configuration file is generated and sent to the machine specified in `host`. The configuration rules of `resource_control` are the same as the `resource_control` content in `global`.

For the above fields, you cannot modify these configured fields after the deployment:

- `host`
- `listen_host`
- `port`
- `status_port`
- `deploy_dir`
- `log_dir`
- `arch`
- `os`

A `tidb_servers` configuration example is as follows:

```yaml
tidb_servers:
  - host: 10.0.1.14
    config:
      log.level: warn
      log.slow-query-file: tidb-slow-overwrited.log
  - host: 10.0.1.15
```
