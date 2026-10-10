# DM master_servers topology fields and immutable settings

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-dm-topology-reference.md`
- Source Title: `Topology Configuration File for DM Cluster Deployment Using TiUP`
- Source Heading Path: `Topology Configuration File for DM Cluster Deployment Using TiUP > `master_servers``
- Source Line Ranges: `84-140`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tiup`, `shared`
- Topic Tags: `master-servers`, `instance-fields`, `port-settings`, `numa`, `config-override`, `resource-control`, `immutable-fields`, `upgrade-path`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_1038_f5bcd736c9`
- Source ID: `tidb-docs-8.1:tiup/tiup-dm-topology-reference.md#master-servers`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `35bab81a2aa9abe38d335f167bbe1669fdc71ffcbb71d3e64c32ff56fc33d851`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-dm-topology-reference#master-servers
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-dm-topology-reference.md

## Retrieval Guidance

- Use When: Use this content when looking up the fields for `master_servers` in a TiUP DM topology file, including per-instance overrides, NUMA binding, and which settings cannot be changed after deployment.
- Retrieval Keywords: master_servers, DM-master instance fields, host, name, port, peer_port, deploy_dir, data_dir, log_dir, numa_node, config, resource_control, v1_source_path, immutable fields after deployment, cannot be modified after deployment, numactl, cpubind, membind, server_configs.master override, upgrade from v1.0.x
- Follow-up Guidance: The source includes a `master_servers` YAML example showing `host`, `name`, ports, directories, `numa_node`, and instance-level `config` overriding `server_configs.master`.
- Classification Note: This is reference content because it lists each `master_servers` field, explains merge and default behavior, and explicitly names the fields that are immutable after deployment.

## Official Source Content

## `master_servers`

`master_servers` specifies the machines to which the master node of the DM component is deployed. You can also specify the service configuration on each machine. `master_servers` is an array. Each array element contains the following fields:

- `host`: specifies the machine to deploy to. The field value is an IP address and is mandatory.
- `ssh_port`: specifies the SSH port to connect to the target machine for operations. If the field is not specified, the `ssh_port` in the `global` section is used.
- `name`: specifies the name of the DM-master instance. The name must be unique for different instances. Otherwise, the cluster cannot be deployed.
- `port`: specifies the port on which DM-master provides services. The default value is "8261".
- `peer_port`: specifies the port for communication between DM-masters. The default value is "8291".
- `deploy_dir`: specifies the deployment directory. If the field is not specified, or specified as a relative directory, the deployment directory is generated according to the `deploy_dir` configuration in the `global` section.
- `data_dir`: specifies the data directory. If the field is not specified, or specified as a relative directory, the data directory is generated according to the `data_dir` configuration in the `global` section.
- `log_dir`: specifies the log directory. If the field is not specified, or specified as a relative directory, the log directory is generated according to the `log_dir` configuration in the `global` section.
- `numa_node`: allocates the NUMA policy to the instance. Before specifying this field, you need to make sure that the target machine has [numactl](https://linux.die.net/man/8/numactl) installed. If this field is specified, cpubind and membind policies are allocated using [numactl](https://linux.die.net/man/8/numactl). This field is a string type. The field value is the ID of the NUMA node, such as "0,1".
- `config`: the configuration rules of this field are the same as that of `master` in the `server_configs` section. If `config` is specified, the configuration of `config` will be merged with the configuration of `master` in `server_configs` (if the two fields overlap, the configuration of this field takes effect), and then the configuration file is generated and distributed to the machine specified in the `host` field.
- `os`: the operating system of the machine specified in the `host` field. If the field is not specified, the default value is the `os` value configured in the `global` section.
- `arch`: the architecture of the machine specified in the `host` field. If the field is not specified, the default value is the `arch` value configured in the `global` section.
- `resource_control`: resource control on this service. If this field is specified, the configuration of this field will be merged with the configuration of `resource_control` in the `global` section (if the two fields overlap, the configuration of this field takes effect), and then the configuration file of systemd is generated and distributed to the machine specified in the `host` field. The configuration rules of this field are the same as that of `resource_control` in the `global` section.
- `v1_source_path`: when upgrading from v1.0.x, you can specify the directory where the configuration file of the V1 source is located in this field.

In the `master_servers` section, the following fields cannot be modified after the deployment is completed: 

- `host`
- `name`
- `port`
- `peer_port`
- `deploy_dir`
- `data_dir`
- `log_dir`
- `arch`
- `os`
- `v1_source_path`

A `master_servers` configuration example is as follows:

```yaml
master_servers:
  - host: 10.0.1.11
    name: master1
    ssh_port: 22
    port: 8261
    peer_port: 8291
    deploy_dir: "/dm-deploy/dm-master-8261"
    data_dir: "/dm-data/dm-master-8261"
    log_dir: "/dm-deploy/dm-master-8261/log"
    numa_node: "0,1"
    # The following configs are used to overwrite the `server_configs.master` values.
    config:
      log-level: info
      rpc-timeout: "30s"
      rpc-rate-limit: 10.0
      rpc-rate-burst: 40
  - host: 10.0.1.18
    name: master2
  - host: 10.0.1.19
    name: master3
```
