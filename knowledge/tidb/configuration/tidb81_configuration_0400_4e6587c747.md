# Update cluster configuration and reload changes

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-cluster.md`
- Source Title: `Deploy and Maintain an Online TiDB Cluster Using TiUP`
- Source Heading Path: `Deploy and Maintain an Online TiDB Cluster Using TiUP > Update configuration`
- Source Line Ranges: `406-463`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `dashboard`, `shared`
- Topic Tags: `configuration`, `reload`, `editor`, `monitoring`, `grafana`, `alertmanager`, `dashboards`, `rules`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0400_4e6587c747`
- Source ID: `tidb-docs-8.1:tiup/tiup-cluster.md#update-configuration`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b9884adeff43bbce8638d662e8262aca4b72f9d1779429d3d0f176b0b910e59d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-cluster#update-configuration
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-cluster.md

## Retrieval Guidance

- Use When: Use this when looking for how to edit a TiUP cluster configuration, apply it with reload, or manage custom monitoring files for Grafana, Prometheus rules, and Alertmanager.
- Retrieval Keywords: tiup cluster edit-config <cluster-name>, tiup cluster reload prod-cluster, EDITOR environment variable, export EDITOR=nano, grafana_servers, dashboard_dir, monitoring_servers, rule_dir, alertmanager_servers, config_file, tiup reload deletes all old configuration files, *.json files, *.rules.yml files, Alertmanager configuration template, tiup cluster rename, tiup cluster reload -R grafana, datasource is named after the cluster name
- Follow-up Guidance: The content also explains that after `tiup reload`, TiUP deletes old configuration files on the target machine before uploading files from the control machine, and it describes extra Grafana dashboard updates needed after `tiup cluster rename` when `dashboard_dir` is configured.
- Classification Note: The classification is configuration because the content covers editing saved cluster configuration, reloading it to take effect, and specifying configuration paths for monitoring components.

## Official Source Content

## Update configuration

If you want to dynamically update the component configurations, the TiUP cluster component saves a current configuration for each cluster. To edit this configuration, execute the `tiup cluster edit-config <cluster-name>` command. For example:

```bash
tiup cluster edit-config prod-cluster
```

TiUP cluster opens the configuration file in the vi editor. If you want to use other editors, use the `EDITOR` environment variable to customize the editor, such as `export EDITOR=nano`.

After editing the file, save the changes. To apply the new configuration to the cluster, execute the following command:

```bash
tiup cluster reload prod-cluster
```

The command sends the configuration to the target machine and restarts the cluster to make the configuration take effect.

> **Note:**
>
> For monitoring components, customize the configuration by executing the `tiup cluster edit-config` command to add a custom configuration path on the corresponding instance. For example:

```yaml
---

grafana_servers:
  - host: 172.16.5.134
    dashboard_dir: /path/to/local/dashboards/dir

monitoring_servers:
  - host: 172.16.5.134
    rule_dir: /path/to/local/rules/dir

alertmanager_servers:
  - host: 172.16.5.134
    config_file: /path/to/local/alertmanager.yml
```

The content and format requirements for files under the specified path are as follows:

- The folder specified in the `dashboard_dir` field of `grafana_servers` must contain full `*.json` files.
- The folder specified in the `rule_dir` field of `monitoring_servers` must contain full `*.rules.yml` files.
- For the format of files specified in the `config_file` field of `alertmanager_servers`, refer to [the Alertmanager configuration template](https://github.com/pingcap/tiup/blob/master/embed/templates/config/alertmanager.yml).

When you execute `tiup reload`, TiUP first deletes all old configuration files in the target machine and then uploads the corresponding configuration from the control machine to the corresponding configuration directory of the target machine. Therefore, if you want to modify a particular configuration file, make sure that all configuration files (including the unmodified ones) are in the same directory. For example, to modify Grafana's `tidb.json` file, you need to first copy all the `*.json` files from Grafana's `dashboards` directory to your local directory. Otherwise, other JSON files will be missing from the target machine.

> **Note:**
>
> If you have configured the `dashboard_dir` field of `grafana_servers`, after executing the `tiup cluster rename` command to rename the cluster, you need to complete the following operations:
>
> 1. In the local `dashboards` directory, change the cluster name to the new cluster name.
> 2. In the local `dashboards` directory, change `datasource` to the new cluster name, because `datasource` is named after the cluster name.
> 3. Execute the `tiup cluster reload -R grafana` command.
