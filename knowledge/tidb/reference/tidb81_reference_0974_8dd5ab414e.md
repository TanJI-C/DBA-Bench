# TiKV-CDC topology section for kvcdc servers

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-cluster-topology-reference.md`
- Source Title: `Topology Configuration File for TiDB Deployment Using TiUP`
- Source Heading Path: `Topology Configuration File for TiDB Deployment Using TiUP > File structure > `kvcdc_servers``
- Source Line Ranges: `571-618`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `tikv`, `pd`, `ticdc`
- Topic Tags: `topology-file`, `kvcdc`, `tikv-cdc`, `server-fields`, `gc-ttl`, `time-zone`, `temporary-storage`, `resource-control`, `immutable-fields`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0974_8dd5ab414e`
- Source ID: `tidb-docs-8.1:tiup/tiup-cluster-topology-reference.md#kvcdc-servers`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f92b68d8fad2ef9ac7cd4e5afa4d519481828f86826a6dd4860366e233bc2058`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-cluster-topology-reference#kvcdc-servers
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-cluster-topology-reference.md

## Retrieval Guidance

- Use When: Use this chunk when you need the TiUP topology reference for `kvcdc_servers`, including host-level fields, default listening port, `gc-ttl`, `tz`, temporary sorting storage, configuration file path, `resource_control`, and immutable fields after deployment.
- Retrieval Keywords: kvcdc_servers, TiKV-CDC, port 8600, gc-ttl, tz, time zone, data-dir, temporary files primarily for sorting, config file address, resource_control, numa_node, deploy_dir, log_dir, immutable fields after deployment
- Follow-up Guidance: The source includes a `kvcdc_servers` YAML example with two hosts.
- Classification Note: This is reference content because it defines the topology configuration fields, defaults, optional settings, and non-modifiable fields for TiKV-CDC servers.

## Official Source Content

### `kvcdc_servers`

`kvcdc_servers` specifies the machines to which the [TiKV-CDC](https://tikv.org/docs/7.1/concepts/explore-tikv-features/cdc/cdc/) services are deployed. It also specifies the service configuration on each machine. `kvcdc_servers` is an array. Each array element contains the following fields:

- `host`: Specifies the machine to which the TiKV-CDC services are deployed. The field value is an IP address and is mandatory.

- `ssh_port`: Specifies the SSH port to connect to the target machine for operations. If it is not specified, the `ssh_port` of the `global` section is used.

- `port`: The listening port of the TiKV-CDC services. The default value is `8600`.

- `deploy_dir`: Specifies the deployment directory. If it is not specified or specified as a relative directory, the directory is generated according to the `deploy_dir` directory configured in `global`.

- `data-dir`: Specifies the directory that TiKV-CDC uses to store temporary files primarily for sorting (optional). The free disk space for this directory is recommended to be greater than or equal to 500 GiB.

- `log_dir`: Specifies the log directory. If it is not specified or specified as a relative directory, the log is generated according to the `log_dir` directory configured in `global`.

- `gc-ttl`: The TTL (Time to Live, in seconds) of the service-level GC safepoint in PD set by TiKV-CDC (optional). It is the duration that replication tasks can be suspended, defaulting to `86400`, which is 24 hours. Note that suspending replication tasks affects the progress of TiKV garbage collection safepoint. The longer the `gc-ttl`, the longer changefeeds can be suspended, but at the same time, more obsolete data will be kept and occupy more space. Vice versa.

- `tz`: The time zone that the TiKV-CDC services use. TiKV-CDC uses this time zone when internally converting time data types such as timestamp and when replicating data to the downstream. The default value is the local time zone where the process runs.

- `numa_node`: Allocates the NUMA policy to the instance. Before specifying this field, you need to make sure that the target machine has [numactl](https://linux.die.net/man/8/numactl) installed. If this field is specified, cpubind and membind policies are allocated using [numactl](https://linux.die.net/man/8/numactl). This field is the string type. The field value is the ID of the NUMA node, such as "0,1".

- `config`: The address of the configuration file that TiKV-CDC uses (optional).

- `os`: The operating system of the machine specified in `host`. If this field is not specified, the default value is the `os` value in `global`.

- `arch`: The architecture of the machine specified in `host`. If this field is not specified, the default value is the `arch` value in `global`.

- `resource_control`: Resource control for the service. If this field is configured, the field content is merged with the `resource_control` content in `global` (if the two fields overlap, the content of this field takes effect). Then, a systemd configuration file is generated and sent to the machine specified in `host`. The configuration rules of `resource_control` are the same as the `resource_control` content in `global`.

For the above fields, you cannot modify these configured fields after the deployment:

- `host`
- `port`
- `deploy_dir`
- `data_dir`
- `log_dir`
- `arch`
- `os`

A `kvcdc_servers` configuration example is as follows:

```yaml
kvcdc_servers:
  - host: 10.0.1.21
  - host: 10.0.1.22
```
