# TiUP topology reference for cdc_servers

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-cluster-topology-reference.md`
- Source Title: `Topology Configuration File for TiDB Deployment Using TiUP`
- Source Heading Path: `Topology Configuration File for TiDB Deployment Using TiUP > File structure > `cdc_servers``
- Source Line Ranges: `619-673`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `pd`, `tiup`, `shared`
- Topic Tags: `topology-file`, `cdc-servers`, `service-configuration`, `deployment-fields`, `immutable-fields`, `gc-ttl`, `timezone`, `numa`, `resource-control`, `cluster-id`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0975_6a396c098a`
- Source ID: `tidb-docs-8.1:tiup/tiup-cluster-topology-reference.md#cdc-servers`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `17ba0d25d112b810aef00e4a267a753606035c4fc025e9fc9e59088b9bb2da50`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-cluster-topology-reference#cdc-servers
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-cluster-topology-reference.md

## Retrieval Guidance

- Use When: Use this chunk when you need the TiUP topology file fields, defaults, merged configuration behavior, or immutable settings for `cdc_servers` that deploy TiCDC services.
- Retrieval Keywords: cdc_servers, TiCDC services, topology configuration file, host, ssh_port, port 8300, deploy_dir, data_dir, log_dir, gc-ttl, GC safepoint, PD, tz, time zone, numa_node, numactl, config, server_configs cdc, resource_control, systemd configuration file, ticdc_cluster_id, default TiCDC cluster, immutable fields
- Follow-up Guidance: The source also states that `ticdc_cluster_id` only takes effect in TiDB v6.3.0 or later versions and provides a `cdc_servers` YAML example with `gc-ttl` and `data_dir`.
- Classification Note: This is a reference section because it enumerates `cdc_servers` topology fields, default values, merge rules, and which fields cannot be modified after deployment.

## Official Source Content

### `cdc_servers`

`cdc_servers` specifies the machines to which the TiCDC services are deployed. It also specifies the service configuration on each machine. `cdc_servers` is an array. Each array element contains the following fields:

- `host`: Specifies the machine to which the TiCDC services are deployed. The field value is an IP address and is mandatory.

- `ssh_port`: Specifies the SSH port to connect to the target machine for operations. If it is not specified, the `ssh_port` of the `global` section is used.

- `port`: The listening port of the TiCDC services. The default value is `8300`.

- `deploy_dir`: Specifies the deployment directory. If it is not specified or specified as a relative directory, the directory is generated according to the `deploy_dir` directory configured in `global`.

- `data_dir`: Specifies the data directory. If it is not specified or specified as a relative directory, the directory is generated according to the `data_dir` directory configured in `global`.

- `log_dir`: Specifies the log directory. If it is not specified or specified as a relative directory, the log is generated according to the `log_dir` directory configured in `global`.

- `gc-ttl`: The Time To Live (TTL) duration of the service level GC safepoint set by TiCDC in PD, in seconds. The default value is `86400`, which is 24 hours.

- `tz`: The time zone that the TiCDC services use. TiCDC uses this time zone when internally converting time data types such as timestamp and when replicating data to the downstream. The default value is the local time zone where the process runs.

- `numa_node`: Allocates the NUMA policy to the instance. Before specifying this field, you need to make sure that the target machine has [numactl](https://linux.die.net/man/8/numactl) installed. If this field is specified, cpubind and membind policies are allocated using [numactl](https://linux.die.net/man/8/numactl). This field is the string type. The field value is the ID of the NUMA node, such as "0,1".

- `config`: The field content is merged with the `cdc` content in `server_configs` (if the two fields overlap, the content of this field takes effect). Then, a configuration file is generated and sent to the machine specified in `host`.

- `os`: The operating system of the machine specified in `host`. If this field is not specified, the default value is the `os` value in `global`.

- `arch`: The architecture of the machine specified in `host`. If this field is not specified, the default value is the `arch` value in `global`.

- `resource_control`: Resource control for the service. If this field is configured, the field content is merged with the `resource_control` content in `global` (if the two fields overlap, the content of this field takes effect). Then, a systemd configuration file is generated and sent to the machine specified in `host`. The configuration rules of `resource_control` are the same as the `resource_control` content in `global`.

- `ticdc_cluster_id`: Specifies the TiCDC cluster ID corresponding to the service. If this field is not specified, the service joins the default TiCDC cluster. This field only takes effect in TiDB v6.3.0 or later versions.

For the above fields, you cannot modify these configured fields after the deployment:

- `host`
- `port`
- `deploy_dir`
- `data_dir`
- `log_dir`
- `arch`
- `os`
- `ticdc_cluster_id`

A `cdc_servers` configuration example is as follows:

```yaml
cdc_servers:
  - host: 10.0.1.20
    gc-ttl: 86400
    data_dir: "/cdc-data"
  - host: 10.0.1.21
    gc-ttl: 86400
    data_dir: "/cdc-data"
```
