# TiProxy topology section in TiUP cluster configuration

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-cluster-topology-reference.md`
- Source Title: `Topology Configuration File for TiDB Deployment Using TiUP`
- Source Heading Path: `Topology Configuration File for TiDB Deployment Using TiUP > File structure > `tiproxy_servers``
- Source Line Ranges: `427-465`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `tiproxy`
- Topic Tags: `topology-file`, `instance-fields`, `deployment-directories`, `ports`, `data-dir`, `numa`, `config-merge`, `immutable-fields`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0972_52a9fe07b1`
- Source ID: `tidb-docs-8.1:tiup/tiup-cluster-topology-reference.md#tiproxy-servers`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0bd693d90d15742956a18c4774b4c4e6111bb2e347cc1dbc6cae586a3108c212`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-cluster-topology-reference#tiproxy-servers
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-cluster-topology-reference.md

## Retrieval Guidance

- Use When: Use this chunk when you need the TiUP topology reference for `tiproxy_servers`, including instance fields, default SQL port, directory settings, NUMA settings, config merging, and fields that cannot be changed after deployment.
- Retrieval Keywords: tiproxy_servers, TiProxy, TiUP topology configuration file, port 6000, deploy_dir, data_dir, numa_node, server_configs tiproxy, host, ssh_port, arch, os, cannot modify after deployment, TiProxy SQL services
- Follow-up Guidance: The source also provides a `tiproxy_servers` YAML example with two hosts.
- Classification Note: This is a reference section because it lists the supported `tiproxy_servers` topology fields, default values, config merge rules, and immutable fields after deployment.

## Official Source Content

### `tiproxy_servers`

`tiproxy_servers` specifies the machines to which the TiProxy services are deployed and the service configuration on each machine. `tiproxy_servers` is an array, and each element of the array contains the following fields:

- `host`: Specifies the IP address of the machine to which the TiProxy services are deployed. This field is mandatory.

- `ssh_port`: Specifies the SSH port to connect to the target machine for operations. If it is not specified, the `ssh_port` of the `global` section is used.

- `port`: The listening port of the TiProxy SQL services. The default value is `6000`.

- `deploy_dir`: Specifies the deployment directory. If it is not specified or specified as a relative directory, the directory is generated based on the `deploy_dir` directory configured in `global`.

- `data_dir`: Specifies the data directory. If it is not specified or specified as a relative directory, the directory is generated based on the `data_dir` directory configured in `global`.

- `numa_node`: Allocates the NUMA policy to the instance. Before specifying this field, you need to make sure that the target machine has [numactl](https://linux.die.net/man/8/numactl) installed. If this field is specified, cpubind and membind policies are allocated using [numactl](https://linux.die.net/man/8/numactl). This field is of string type. The value is the ID of the NUMA node, such as `"0,1"`.

- `config`: The configuration rule of this field is the same as the `tiproxy` configuration rule in `server_configs`. If this field is configured, the field content is merged with the `tiproxy` content in `server_configs`. If these two fields overlap, the content of this field takes effect. Subsequently, a configuration file is generated and sent to the machine specified in `host`.

- `os`: The operating system of the machine specified in `host`. If this field is not specified, the default value is the `os` value in `global`.

- `arch`: The architecture of the machine specified in `host`. If this field is not specified, the default value is the `arch` value in `global`.

Among the above fields, you cannot modify the following configured fields after the deployment:

- `host`
- `port`
- `deploy_dir`
- `data_dir`
- `arch`
- `os`

A `tiproxy_servers` configuration example is as follows:

```yaml
tiproxy_servers:
  - host: 10.0.1.21
  - host: 10.0.1.22
```
