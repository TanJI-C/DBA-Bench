# Grafana_servers topology and post-rename dashboard handling

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-dm-topology-reference.md`
- Source Title: `Topology Configuration File for DM Cluster Deployment Using TiUP`
- Source Heading Path: `Topology Configuration File for DM Cluster Deployment Using TiUP > `worker_servers` > `grafana_servers``
- Source Line Ranges: `239-276`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `dm`, `tiup`, `dashboard`
- Topic Tags: `grafana-servers`, `topology`, `dashboards`, `authentication`, `cluster-rename`, `reload`, `immutability`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0125_a84227fd41`
- Source ID: `tidb-docs-8.1:tiup/tiup-dm-topology-reference.md#grafana-servers`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `cdbc815ac01a9f6dee217052e571e156b272274a0b51770ad097b4e52647c5af`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-dm-topology-reference#grafana-servers
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-dm-topology-reference.md

## Retrieval Guidance

- Use When: Use this when describing `grafana_servers` topology fields in TiUP DM deployments, especially dashboard provisioning, Grafana login fields, immutable fields, and the note about cluster rename handling.
- Retrieval Keywords: grafana_servers, Grafana, host, ssh_port, port, deploy_dir, username, password, dashboard_dir, resource_control, tiup cluster rename, tiup cluster reload -R grafana, datasource, fields cannot be modified after the deployment is completed
- Follow-up Guidance: If `dashboard_dir` is configured and `tiup cluster rename` is executed, the source says to update the local dashboards `datasource` field to the new cluster name and then run `tiup cluster reload -R grafana`.
- Classification Note: This is classified as observability because the content defines Grafana deployment and dashboard configuration used for cluster visualization and monitoring.

## Official Source Content

### `grafana_servers`

`grafana_servers` specifies the machines to which the Grafana service is deployed. You can also specify the service configuration on the machine. `grafana_servers` is an array. Each array element contains the following fields:

- `host`: specifies the machine to deploy to. The field value is an IP address and is mandatory.
- `ssh_port`: specifies the SSH port to connect to the target machine for operations. If the field is not specified, the `ssh_port` in the `global` section is used.
- `port`: specifies the port on which Grafana provides services. The default value is "3000".
- `deploy_dir`: specifies the deployment directory. If the field is not specified, or specified as a relative directory, the deployment directory is generated according to the `deploy_dir` configuration in the `global` section.
- `os`: the operating system of the machine specified in the `host` field. If the field is not specified, the default value is the `os` value configured in the `global` section.
- `arch`: the architecture of the machine specified in the `host` field. If the field is not specified, the default value is the `arch` value configured in the `global` section.
- `username`: specifies the username of the Grafana login screen.
- `password`: specifies the corresponding password of Grafana.
- `dashboard_dir`: specifies a local directory where the complete `dashboard(*.json)` files are located. The files in the specified directory will be sent to the target machine as Grafana dashboards during the initialization phase of the cluster configuration.
- `resource_control`: resource control on this service. If this field is specified, the configuration of this field will be merged with the configuration of `resource_control` in the `global` section (if the two fields overlap, the configuration of this field takes effect), and then the configuration file of systemd is generated and distributed to the machine specified in the `host` field. The configuration rules of this field are the same as that of `resource_control` in the `global` section.

> **Note:**
>
> If the `dashboard_dir` field of `grafana_servers` is configured, after executing the `tiup cluster rename` command to rename the cluster, you need to perform the following operations:
>
> 1. In the local `dashboards` directory, update the value of the `datasource` field to the new cluster name (the `datasource` is named after the cluster name).
> 2. Execute the `tiup cluster reload -R grafana` command.

In `grafana_servers`, the following fields cannot be modified after the deployment is completed:

- `host`
- `port`
- `deploy_dir`
- `arch`
- `os`

A `grafana_servers` configuration example is as follows:

```yaml
grafana_servers:
  - host: 10.0.1.11
    dashboard_dir: /local/dashboard/dir
```
