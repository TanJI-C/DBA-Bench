# Monitoring_servers topology for Prometheus in DM clusters

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-dm-topology-reference.md`
- Source Title: `Topology Configuration File for DM Cluster Deployment Using TiUP`
- Source Heading Path: `Topology Configuration File for DM Cluster Deployment Using TiUP > `worker_servers` > `monitoring_servers``
- Source Line Ranges: `185-238`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `dm`, `tiup`
- Topic Tags: `monitoring-servers`, `prometheus`, `topology`, `remote-write`, `remote-read`, `alertmanager`, `retention`, `rules`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0124_a1f11eabb3`
- Source ID: `tidb-docs-8.1:tiup/tiup-dm-topology-reference.md#monitoring-servers`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `dccd6e36713c6e2b3cb2f295609fa1786c37c15e83ce206497da606063f87a7b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-dm-topology-reference#monitoring-servers
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-dm-topology-reference.md

## Retrieval Guidance

- Use When: Use this when describing `monitoring_servers` topology for Prometheus in a DM cluster, including retention, rule files, remote read or write, external Alertmanager targets, and immutable fields.
- Retrieval Keywords: monitoring_servers, Prometheus, host, ssh_port, port, deploy_dir, data_dir, log_dir, numa_node, storage_retention, rule_dir, remote_config, remote_write, remote_read, external_alertmanagers, Alertmanager, resource_control, fields cannot be modified after the deployment is completed
- Follow-up Guidance: The source includes a `monitoring_servers` YAML example with `rule_dir`, `remote_config.remote_write`, `remote_config.remote_read`, and `external_alertmanagers` entries using `host` and `web_port`.
- Classification Note: This is classified as observability because the content configures the Prometheus monitoring service and its alerting, retention, and remote read or write integration settings.

## Official Source Content

### `monitoring_servers`

`monitoring_servers` specifies the machines to which the Prometheus service is deployed. You can also specify the service configuration on the machine. `monitoring_servers` is an array. Each array element contains the following fields:

- `host`: specifies the machine to deploy to. The field value is an IP address and is mandatory.
- `ssh_port`: specifies the SSH port to connect to the target machine for operations. If the field is not specified, the `ssh_port` in the `global` section is used.
- `port`: specifies the port on which Prometheus provides services. The default value is "9090".
- `deploy_dir`: specifies the deployment directory. If the field is not specified, or specified as a relative directory, the deployment directory is generated according to the `deploy_dir` configuration in the `global` section.
- `data_dir`: specifies the data directory. If the field is not specified, or specified as a relative directory, the data directory is generated according to the `data_dir` configuration in the `global` section.
- `log_dir`: specifies the log directory. If the field is not specified, or specified as a relative directory, the log directory is generated according to the `log_dir` configuration in the `global` section.
- `numa_node`: allocates the NUMA policy to the instance. Before specifying this field, you need to make sure that the target machine has [numactl](https://linux.die.net/man/8/numactl) installed. If this field is specified, cpubind and membind policies are allocated using [numactl](https://linux.die.net/man/8/numactl). This field is a string type. The field value is the ID of the NUMA node, such as "0,1"
- `storage_retention`: specifies the retention time of the Prometheus monitoring data. The default value is "15d".
- `rule_dir`: specifies a local directory where the complete `*.rules.yml` files are located. The files in the specified directory will be sent to the target machine as the Prometheus rules during the initialization phase of the cluster configuration.
- `remote_config`: Supports writing Prometheus data to the remote, or reading data from the remote. This field has two configurations:
    - `remote_write`: See the Prometheus document [`<remote_write>`](https://prometheus.io/docs/prometheus/latest/configuration/configuration/#remote_write).
    - `remote_read`: See the Prometheus document [`<remote_read>`](https://prometheus.io/docs/prometheus/latest/configuration/configuration/#remote_read).
- `external_alertmanagers`: If the `external_alertmanagers` field is configured, Prometheus alerts the configuration behavior to the Alertmanager that is outside the cluster. This field is an array, each element of which is an external Alertmanager and consists of the `host` and `web_port` fields.
- `os`: the operating system of the machine specified in the `host` field. If the field is not specified, the default value is the `os` value configured in the `global` section.
- `arch`: the architecture of the machine specified in the `host` field. If the field is not specified, the default value is the `arch` value configured in the `global` section.
- `resource_control`: resource control on this service. If this field is specified, the configuration of this field will be merged with the configuration of `resource_control` in the `global` section (if the two fields overlap, the configuration of this field takes effect), and then the configuration file of systemd is generated and distributed to the machine specified in the `host` field. The configuration rules of this field are the same as that of `resource_control` in the `global` section.

In the `monitoring_servers` section, the following fields cannot be modified after the deployment is completed: 

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
    remote_config:
      remote_write:
      - queue_config:
          batch_send_deadline: 5m
          capacity: 100000
          max_samples_per_send: 10000
          max_shards: 300
        url: http://127.0.0.1:8003/write
      remote_read:
      - url: http://127.0.0.1:8003/read\
      external_alertmanagers:
      - host: 10.1.1.1
      web_port: 9093
      - host: 10.1.1.2
      web_port: 9094
```
