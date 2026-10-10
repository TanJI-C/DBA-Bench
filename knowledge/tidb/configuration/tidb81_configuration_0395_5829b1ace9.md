# TiUP-managed monitoring server configuration customization

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/customized-montior-in-tiup-environment.md`
- Source Title: `Customize Configurations of Monitoring Servers`
- Source Heading Path: `Customize Configurations of Monitoring Servers | Customize Configurations of Monitoring Servers > Customize Prometheus configurations | Customize Configurations of Monitoring Servers > Customize Prometheus configurations > Customize Prometheus rule configuration | Customize Configurations of Monitoring Servers > Customize Prometheus configurations > Customize Prometheus scrape configuration | Customize Configurations of Monitoring Servers > Customize Grafana configurations | Customize Configurations of Monitoring Servers > Customize Grafana configurations > Customize Grafana Dashboard | Customize Configurations of Monitoring Servers > Customize Grafana configurations > Customize other Grafana configurations | Customize Configurations of Monitoring Servers > Customize Alertmanager configurations`
- Source Line Ranges: `5-138`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `shared`
- Topic Tags: `monitoring`, `prometheus`, `grafana`, `alertmanager`, `topology.yaml`, `rule_dir`, `additional_scrape_conf`, `dashboard_dir`, `listen_host`, `reload`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0395_5829b1ace9`
- Source ID: `tidb-docs-8.1:tiup/customized-montior-in-tiup-environment.md#customize-configurations-of-monitoring-servers`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ae9f747e623820ecb9dcbea88d0b57120912db69607bfbc880143aa2c06bc8b3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/customized-montior-in-tiup-environment#customize-configurations-of-monitoring-servers
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/customized-montior-in-tiup-environment.md

## Retrieval Guidance

- Use When: Use this chunk when you need the supported topology.yaml fields for customizing TiUP-managed monitoring servers such as Prometheus, Grafana, or Alertmanager in a TiDB cluster.
- Retrieval Keywords: TiUP-managed monitoring server configuration customization, topology.yaml, monitoring_servers, grafana_servers, alertmanager_servers, rule_dir, additional_scrape_conf, dashboard_dir, config, listen_host, grafana.ini, --web.listen-address, Prometheus rule configuration, Prometheus scrape configuration, Grafana Dashboard, Alertmanager listening address, deploy scale out scale in reload
- Follow-up Guidance: The source notes not to modify monitoring server configuration files directly because later TiUP operations such as deployment, scaling out, scaling in, and reloading overwrite those changes.
- Classification Note: This is classified as configuration because the content defines topology.yaml settings for TiUP-managed Prometheus, Grafana, and Alertmanager customization, including rule_dir, additional_scrape_conf, dashboard_dir, config, and listen_host.

## Official Source Content

# Customize Configurations of Monitoring Servers

When you deploy a TiDB cluster using TiUP, TiUP also deploys monitoring servers, such as Prometheus, Grafana, and Alertmanager. In the meantime, if you scale out this cluster, TiUP also adds the new nodes into monitoring scope.

To customize the configurations of the monitoring servers mentioned above, you can follow the instructions below to add related configuration items in the topology.yaml of the TiDB cluster.

> **Note:**
>
> - Do not modify the configurations files of the monitoring server directly. Because these modifications will be overwritten by later TiUP operations such as deployment, scaling out, scaling in, and reloading.
>
> - If your monitoring servers are not deployed and managed by TiUP, you can directly modify the configuration files of the monitoring servers instead of referring to this document.
>
> - This feature is supported in TiUP v1.9.0 and above. Therefore, check the TiUP version before using this feature.
## Customize Prometheus configurations

Currently, TiUP supports customizing Prometheus rule and scrape configuration files.
### Customize Prometheus rule configuration

1. Customize the rule configuration file and place it under a directory of the machine where TiUP locates.

2. In the topology.yaml file, set `rule_dir` to the directory of the customized rule configuration file.

    The following is a configuration example of monitoring_servers in the topology.yaml file:

    ```
    # # Server configs are used to specify the configuration of Prometheus Server.
    monitoring_servers:
      # # The ip address of the Monitoring Server.
    - host: 127.0.0.1
      rule_dir: /home/tidb/prometheus_rule   # prometheus rule dir on TiUP machine
    ```

After the preceding configuration is done, when you deploy, scale out, scale in, or reload a TiDB cluster, TiUP loads the customized rule configurations from `rule_dir` (for example, `/home/tidb/prometheus_rule`) and sends them to the Prometheus Server to replace the default rule configuration.
### Customize Prometheus scrape configuration

1. Open the topology.yaml file of the TiDB cluster.

2. In the `monitoring_servers` configuration, add the `additional_scrape_conf` field.

    The following is a configuration example of monitoring_servers in the topology.yaml file:

    ```
    monitoring_servers:
    - host: xxxxxxx
    ssh_port: 22
    port: 9090
    deploy_dir: /tidb-deploy/prometheus-9090
    data_dir: /tidb-data/prometheus-9090
    log_dir: /tidb-deploy/prometheus-9090/log
    external_alertmanagers: []
    arch: amd64
    os: linux
    additional_scrape_conf:
      metric_relabel_configs:
        - source_labels: [__name__]
            separator: ;
            regex: tikv_thread_nonvoluntary_context_switches|tikv_thread_voluntary_context_switches|tikv_threads_io_bytes_total
            action: drop
        - source_labels: [__name__,name]
            separator: ;
            regex: tikv_thread_cpu_seconds_total;(tokio|rocksdb).+
            action: drop
    ```

After the preceding configuration is done, when you deploy, scale out, scale in, or reload a TiDB cluster, TiUP adds the content of the `additional_scrape_conf` field to the corresponding parameters of the Prometheus configuration file.
## Customize Grafana configurations

Currently, TiUP supports customizing Grafana Dashboard and other configurations.
### Customize Grafana Dashboard

1. Customize the configuration file of the Grafana Dashboard and place it under a directory of the machine where TiUP locates.

2. In the topology.yaml file, set `dashboard_dir` to the directory of the customized Dashboard configuration file.

    The following is a configuration example of grafana_servers in the topology.yaml file:

    ```
    # # Server configs are used to specify the configuration of Grafana Servers.
    grafana_servers:
      # # The ip address of the Grafana Server.
     - host: 127.0.0.1
     dashboard_dir: /home/tidb/dashboards   # grafana dashboard dir on TiUP machine
    ```

After the preceding configuration is done, when you deploy, scale out, scale in, or reload a TiDB cluster, TiUP loads the customized Dashboard configurations from `dashboard_dir` (for example, `/home/tidb/dashboards`) and sends the configurations to the Grafana Server to replace the default Dashboard configuration.
### Customize other Grafana configurations

1. Open the topology.yaml file of the TiDB cluster.

2. Add other configuration items in the `grafana_servers` configuration.

    The following is a configuration example of the `[log.file] level` and `smtp` fields in the topology.yaml file:

    ```
    # # Server configs are used to specify the configuration of Grafana Servers.
    grafana_servers:
    # # The ip address of the Grafana Server.
    - host: 127.0.0.1
        config:
        log.file.level: warning
        smtp.enabled: true
        smtp.host: {IP}:{port}
        smtp.user: example@pingcap.com
        smtp.password: {password}
        smtp.skip_verify: true
    ```

After the preceding configuration is done, when you deploy, scale out, scale in, or reload a TiDB cluster, TiUP adds the content of the `config` field to the Grafana configuration file `grafana.ini`.
## Customize Alertmanager configurations

Currently, TiUP supports customizing the listening address of Alertmanager.

Alertmanager deployed by TiUP listens to `alertmanager_servers.host` by default. You cannot access Alertmanager if you use a proxy. To address this issue, you can specify the listening address by adding `listen_host` to the cluster configuration file topology.yaml. The recommended value is 0.0.0.0.

The following example sets the `listen_host` field to 0.0.0.0.

```
alertmanager_servers:
  # # The ip address of the Alertmanager Server.
  - host: 172.16.7.147
    listen_host: 0.0.0.0
    # # SSH port of the server.
    ssh_port: 22
```

After the preceding configuration is done, when you deploy, scale out, scale in, or reload a TiDB cluster, TiUP adds the content of the `listen_host` field to `--web.listen-address` in Alertmanager startup parameters.
