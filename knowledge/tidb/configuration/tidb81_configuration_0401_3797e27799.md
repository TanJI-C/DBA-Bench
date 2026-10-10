# DM worker_servers topology fields and immutability

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-dm-topology-reference.md`
- Source Title: `Topology Configuration File for DM Cluster Deployment Using TiUP`
- Source Heading Path: `Topology Configuration File for DM Cluster Deployment Using TiUP > `worker_servers``
- Source Line Ranges: `141-184`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tiup`, `shared`
- Topic Tags: `topology`, `worker-servers`, `deployment`, `instance-configuration`, `directories`, `numa`, `resource-control`, `immutability`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0401_3797e27799`
- Source ID: `tidb-docs-8.1:tiup/tiup-dm-topology-reference.md#worker-servers`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `16e6b1f6433bd56d98860fa3eb1ea3a73de01ec6a11001c1f5481268b62c7f9a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-dm-topology-reference#worker-servers
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-dm-topology-reference.md

## Retrieval Guidance

- Use When: Use this when describing TiUP DM topology fields for `worker_servers`, including per-instance settings, merge behavior with `server_configs.worker`, and which fields are immutable after deployment.
- Retrieval Keywords: worker_servers, DM-worker, host, ssh_port, name, port, deploy_dir, data_dir, log_dir, numa_node, config, server_configs.worker, resource_control, os, arch, fields cannot be modified after the deployment is completed, numactl
- Follow-up Guidance: The source includes a `worker_servers` YAML example showing `host`, `ssh_port`, `port`, `deploy_dir`, `log_dir`, `numa_node`, and `config` overriding `server_configs.worker` values.
- Classification Note: This is classified as configuration because the content defines the `worker_servers` topology schema, field meanings, merge rules, defaults, and immutable fields for DM deployment.

## Official Source Content

## `worker_servers`

`worker_servers` specifies the machines to which the master node of the DM component is deployed. You can also specify the service configuration on each machine. `worker_servers` is an array. Each array element contains the following fields:

- `host`: specifies the machine to deploy to. The field value is an IP address and is mandatory.
- `ssh_port`: specifies the SSH port to connect to the target machine for operations. If the field is not specified, the `ssh_port` in the `global` section is used.
- `name`: specifies the name of the DM-worker instance. The name must be unique for different instances. Otherwise, the cluster cannot be deployed.
- `port`: specifies the port on which DM-worker provides services. The default value is "8262".
- `deploy_dir`: specifies the deployment directory. If the field is not specified, or specified as a relative directory, the deployment directory is generated according to the `deploy_dir` configuration in the `global` section.
- `data_dir`: specifies the data directory. If the field is not specified, or specified as a relative directory, the data directory is generated according to the `data_dir` configuration in the `global` section.
- `log_dir`: specifies the log directory. If the field is not specified, or specified as a relative directory, the log directory is generated according to the `log_dir` configuration in the `global` section.
- `numa_node`: allocates the NUMA policy to the instance. Before specifying this field, you need to make sure that the target machine has [numactl](https://linux.die.net/man/8/numactl) installed. If this field is specified, cpubind and membind policies are allocated using [numactl](https://linux.die.net/man/8/numactl). This field is a string type. The field value is the ID of the NUMA node, such as "0,1".
- `config`: the configuration rules of this field are the same as that of `worker` in the `server_configs` section. If `config` is specified, the configuration of `config` will be merged with the configuration of `worker` in `server_configs` (if the two fields overlap, the configuration of this field takes effect), and then the configuration file is generated and distributed to the machine specified in the `host` field.
- `os`: the operating system of the machine specified in the `host` field. If the field is not specified, the default value is the `os` value configured in the `global` section.
- `arch`: the architecture of the machine specified in the `host` field. If the field is not specified, the default value is the `arch` value configured in the `global` section.
- `resource_control`: resource control on this service. If this field is specified, the configuration of this field will be merged with the configuration of `resource_control` in the `global` section (if the two fields overlap, the configuration of this field takes effect), and then the configuration file of systemd is generated and distributed to the machine specified in the `host` field. The configuration rules of this field are the same as that of `resource_control` in the `global` section.

In the `worker_servers` section, the following fields cannot be modified after the deployment is completed: 

- `host`
- `name`
- `port`
- `deploy_dir`
- `data_dir`
- `log_dir`
- `arch`
- `os`

A `worker_servers` configuration example is as follows:

```yaml
worker_servers:
  - host: 10.0.1.12
    ssh_port: 22
    port: 8262
    deploy_dir: "/dm-deploy/dm-worker-8262"
    log_dir: "/dm-deploy/dm-worker-8262/log"
    numa_node: "0,1"
    # config is used to overwrite the `server_configs.worker` values
    config:
      log-level: info
  - host: 10.0.1.19
```
