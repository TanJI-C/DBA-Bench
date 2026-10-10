# TiUP topology reference for monitoring_servers Prometheus settings

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-cluster-topology-reference.md`
- Source Title: `Topology Configuration File for TiDB Deployment Using TiUP`
- Source Heading Path: `Topology Configuration File for TiDB Deployment Using TiUP > File structure > `monitoring_servers``
- Source Line Ranges: `771-843`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `shared`
- Topic Tags: `topology-file`, `prometheus`, `monitoring`, `ngmonitoring`, `top-sql`, `continuous-profiling`, `remote-write`, `remote-read`, `alertmanager`, `resource-control`, `numa`, `scrape-configuration`, `immutability`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0977_9836a2c9aa`
- Source ID: `tidb-docs-8.1:tiup/tiup-cluster-topology-reference.md#monitoring-servers`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a28f57f8838b194c3284be9123ca27d202cb3cd76cf77a1d692153a61bbda796`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-cluster-topology-reference#monitoring-servers
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-cluster-topology-reference.md

## Retrieval Guidance

- Use When: Use this when looking up the `monitoring_servers` section of a TiUP topology file for Prometheus deployment fields, NgMonitoring settings, remote read or write, alerting, scrape customization, or immutable monitoring server fields.
- Retrieval Keywords: monitoring_servers, Prometheus services, ng_port, NgMonitoring, Continuous Profiling, Top SQL, port 9090, storage_retention, rule_dir, remote_config, remote_write, remote_read, external_alertmanagers, resource_control, additional_args, --web.enable-lifecycle, additional_scrape_conf, Customize Prometheus scrape configuration, numa_node, numactl, immutable fields host port deploy_dir data_dir log_dir arch os
- Follow-up Guidance: The source also includes a `monitoring_servers` YAML example showing `rule_dir`, `additional_args`, `remote_config` with `remote_write` and `remote_read`, and `external_alertmanagers` entries.
- Classification Note: This is reference content because it enumerates the available `monitoring_servers` topology fields, defaults, behavior, and the fields that cannot be modified after deployment.

## Official Source Content

### `monitoring_servers`

`monitoring_servers` specifies the machines to which the Prometheus services are deployed. It also specifies the service configuration on each machine. `monitoring_servers` is an array. Each array element contains the following fields:

- `host`: Specifies the machine to which the monitoring services are deployed. The field value is an IP address and is mandatory.

- `ng_port`: Specifies the port that NgMonitoring listens to. Introduced in TiUP v1.7.0, this field supports [Continuous Profiling](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-profiling) and [Top SQL](https://docs.pingcap.com/tidb/stable/dashboard/top-sql). The default value is `12020`.

- `ssh_port`: Specifies the SSH port to connect to the target machine for operations. If it is not specified, the `ssh_port` of the `global` section is used.

- `port`: The listening port of the Prometheus services. The default value is `9090`.

- `deploy_dir`: Specifies the deployment directory. If it is not specified or specified as a relative directory, the directory is generated according to the `deploy_dir` directory configured in `global`.

- `data_dir`: Specifies the data directory. If it is not specified or specified as a relative directory, the directory is generated according to the `data_dir` directory configured in `global`.

- `log_dir`: Specifies the log directory. If it is not specified or specified as a relative directory, the log is generated according to the `log_dir` directory configured in `global`.

- `numa_node`: Allocates the NUMA policy to the instance. Before specifying this field, you need to make sure that the target machine has [numactl](https://linux.die.net/man/8/numactl) installed. If this field is specified, cpubind and membind policies are allocated using [numactl](https://linux.die.net/man/8/numactl). This field is the string type. The field value is the ID of the NUMA node, such as "0,1".

- `storage_retention`: The retention time of the Prometheus monitoring data. The default value is `"30d"`.

- `rule_dir`: Specifies a local directory that should contain complete `*.rules.yml` files. These files are transferred to the target machine during the initialization phase of the cluster configuration as the rules for Prometheus.
- `remote_config`: Supports writing Prometheus data to the remote, or reading data from the remote. This field has two configurations:
    - `remote_write`: See the Prometheus document [`<remote_write>`](https://prometheus.io/docs/prometheus/latest/configuration/configuration/#remote_write).
    - `remote_read`: See the Prometheus document [`<remote_read>`](https://prometheus.io/docs/prometheus/latest/configuration/configuration/#remote_read).
- `external_alertmanagers`: If the `external_alertmanagers` field is configured, Prometheus alerts the configuration behavior to the Alertmanager that is outside the cluster. This field is an array, each element of which is an external Alertmanager and consists of the `host` and `web_port` fields.

- `os`: The operating system of the machine specified in `host`. If this field is not specified, the default value is the `os` value in `global`.

- `arch`: The architecture of the machine specified in `host`. If this field is not specified, the default value is the `arch` value in `global`.

- `resource_control`: Resource control for the service. If this field is configured, the field content is merged with the `resource_control` content in `global` (if the two fields overlap, the content of this field takes effect). Then, a systemd configuration file is generated and sent to the machine specified in `host`. The configuration rules of `resource_control` are the same as the `resource_control` content in `global`.

- `additional_args`: Introduced in TiUP v1.15.0, this field configures additional parameters for running Prometheus. This field is an array, and each element of the array is a Prometheus running parameter. For example, to enable the Prometheus hot reload feature, you can set this field to `--web.enable-lifecycle`.

- `additional_scrape_conf`: Customized Prometheus scrape configuration. When you deploy, scale out, scale in, or reload a TiDB cluster, TiUP adds the content of the `additional_scrape_conf` field to the corresponding parameters of the Prometheus configuration file. For more information, see [Customize Prometheus scrape configuration](https://docs.pingcap.com/tidb/stable/tiup/customized-montior-in-tiup-environment#customize-prometheus-scrape-configuration).

For the above fields, you cannot modify these configured fields after the deployment:

- `host`
- `port`
- `deploy_dir`
- `data_dir`
- `log_dir`
- `arch`
- `os`

A `monitoring_servers` configuration example is as follows:

```yaml
monitoring_servers:
  - host: 10.0.1.11
    rule_dir: /local/rule/dir
    additional_args:
    - --web.enable-lifecycle
    remote_config:
      remote_write:
      - queue_config:
          batch_send_deadline: 5m
          capacity: 100000
          max_samples_per_send: 10000
          max_shards: 300
        url: http://127.0.0.1:8003/write
      remote_read:
      - url: http://127.0.0.1:8003/read
      external_alertmanagers:
      - host: 10.1.1.1
        web_port: 9093
      - host: 10.1.1.2
        web_port: 9094
```
