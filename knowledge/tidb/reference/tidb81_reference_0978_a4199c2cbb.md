# TiUP topology reference for grafana_servers settings

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-cluster-topology-reference.md`
- Source Title: `Topology Configuration File for TiDB Deployment Using TiUP`
- Source Heading Path: `Topology Configuration File for TiDB Deployment Using TiUP > File structure > `grafana_servers``
- Source Line Ranges: `844-892`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `shared`
- Topic Tags: `topology-file`, `grafana`, `dashboards`, `authentication`, `resource-control`, `config-file`, `cluster-rename`, `reload`, `immutability`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0978_a4199c2cbb`
- Source ID: `tidb-docs-8.1:tiup/tiup-cluster-topology-reference.md#grafana-servers`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5b5dc7c1551dc71c46c9fe3ae3a24dfae0967a5e90f3d51220a532bb93c99526`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-cluster-topology-reference#grafana-servers
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-cluster-topology-reference.md

## Retrieval Guidance

- Use When: Use this when looking up the `grafana_servers` section of a TiUP topology file for Grafana deployment fields, login settings, dashboard import directory, custom `grafana.ini` configuration, rename-related dashboard updates, or immutable Grafana server fields.
- Retrieval Keywords: grafana_servers, Grafana services, port 3000, username, password, dashboard_dir, dashboard(*.json), resource_control, config, grafana.ini, Customize other Grafana configurations, tiup cluster rename, datasource field, tiup cluster reload -R grafana, immutable fields host port deploy_dir arch os
- Follow-up Guidance: If `dashboard_dir` is configured and `tiup cluster rename` is executed, the source says to update each dashboard `datasource` value to the new cluster name and then run `tiup cluster reload -R grafana`.
- Classification Note: This is reference content because it lists the `grafana_servers` topology fields, describes how custom dashboard and config content is applied, and states which fields cannot be changed after deployment.

## Official Source Content

### `grafana_servers`

`grafana_servers` specifies the machines to which the Grafana services are deployed. It also specifies the service configuration on each machine. `grafana_servers` is an array. Each array element contains the following fields:

- `host`: Specifies the machine to which the Grafana services are deployed. The field value is an IP address and is mandatory.

- `ssh_port`: Specifies the SSH port to connect to the target machine for operations. If it is not specified, the `ssh_port` of the `global` section is used.

- `port`: The listening port of the Grafana services. The default value is `3000`.

- `deploy_dir`: Specifies the deployment directory. If it is not specified or specified as a relative directory, the directory is generated according to the `deploy_dir` directory configured in `global`.

- `os`: The operating system of the machine specified in `host`. If this field is not specified, the default value is the `os` value in `global`.

- `arch`: The architecture of the machine specified in `host`. If this field is not specified, the default value is the `arch` value in `global`.

- `username`: The user name on the Grafana login interface.

- `password`: The password corresponding to Grafana.

- `dashboard_dir`: Specifies a local directory that should contain complete `dashboard(*.json)` files. These files are transferred to the target machine during the initialization phase of the cluster configuration as the dashboards for Grafana.

- `resource_control`: Resource control for the service. If this field is configured, the field content is merged with the `resource_control` content in `global` (if the two fields overlap, the content of this field takes effect). Then, a systemd configuration file is generated and sent to the machine specified in `host`. The configuration rules of `resource_control` are the same as the `resource_control` content in `global`.

- `config`: This field is used to add custom configurations to Grafana. When you deploy, scale out, scale in, or reload a TiDB cluster, TiUP adds the content of the `config` field to the Grafana configuration file `grafana.ini`. For more information, see [Customize other Grafana configurations](https://docs.pingcap.com/tidb/stable/tiup/customized-montior-in-tiup-environment#customize-other-grafana-configurations).

> **Note:**
>
> If the `dashboard_dir` field of `grafana_servers` is configured, after executing the `tiup cluster rename` command to rename the cluster, you need to perform the following operations:
>
> 1. For the `*.json` files in the local dashboards directory, update the value of the `datasource` field to the new cluster name (because `datasource` is named after the cluster name).
> 2. Execute the `tiup cluster reload -R grafana` command.

For the above fields, you cannot modify these configured fields after the deployment:

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
