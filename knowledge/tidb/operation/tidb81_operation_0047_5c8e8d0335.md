# Manual deployment of Prometheus, node_exporter, and Grafana

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/deploy-monitoring-services.md`
- Source Title: `Deploy Monitoring Services for the TiDB Cluster`
- Source Heading Path: `Deploy Monitoring Services for the TiDB Cluster | Deploy Monitoring Services for the TiDB Cluster > Deploy Prometheus and Grafana | Deploy Monitoring Services for the TiDB Cluster > Deploy Prometheus and Grafana > Step 1: Download the binary package | Deploy Monitoring Services for the TiDB Cluster > Deploy Prometheus and Grafana > Step 2: Start `node_exporter` on Node1, Node2, Node3, and Node4 | Deploy Monitoring Services for the TiDB Cluster > Deploy Prometheus and Grafana > Step 3: Start Prometheus on Node1 | Deploy Monitoring Services for the TiDB Cluster > Deploy Prometheus and Grafana > Step 4: Start Grafana on Node1`
- Source Line Ranges: `5-206`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `dashboard`, `pd`, `tidb`, `tikv`, `tiflash`, `ticdc`, `lightning`, `tiup`
- Topic Tags: `monitoring`, `prometheus`, `grafana`, `node_exporter`, `manual-deployment`, `alert-rules`, `metrics-scraping`, `topology`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0047_5c8e8d0335`
- Source ID: `tidb-docs-8.1:deploy-monitoring-services.md#deploy-monitoring-services-for-the-tidb-cluster`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e97d2d52eebb5dd0597bd65eeb94a10c6645a41aa66deffc3e52aebd5a68bd9b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/deploy-monitoring-services#deploy-monitoring-services-for-the-tidb-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/deploy-monitoring-services.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving manual self-managed deployment steps for Prometheus, node_exporter, and Grafana for a TiDB cluster, including Prometheus scrape targets and alert rule file configuration.
- Retrieval Keywords: manual deployment of Prometheus Grafana node_exporter, Deploy Monitoring Services for the TiDB Cluster, node_exporter --web.listen-address=:9100, prometheus.yml, scrape_configs, job_name: 'tidb', job_name: 'pd', job_name: 'tikv', job_name: 'overwritten-nodes', rule_files, tidb.rules.yml, pd.rules.yml, tikv.rules.yml, tiflash.rules.yml, ticdc.rules.yml, lightning.rules.yml, ./prometheus --config.file=./prometheus.yml, --web.listen-address=:9090, grafana.ini, ./bin/grafana-server --config=./conf/grafana.ini, TiDB Dashboard is built into the PD component
- Follow-up Guidance: The source continues with Grafana configuration steps for adding a Prometheus data source, importing dashboard JSON files, and viewing component metrics.
- Classification Note: The official content is classified as operation because it provides manual deployment procedures, startup commands, topology examples, and configuration snippets for monitoring services.

## Official Source Content

# Deploy Monitoring Services for the TiDB Cluster

This document is intended for users who want to manually deploy TiDB monitoring and alert services. If you deploy the TiDB cluster using TiUP, the monitoring and alert services are automatically deployed, and no manual deployment is needed. [TiDB Dashboard](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-intro) is built into the PD component and does not require an independent deployment.
## Deploy Prometheus and Grafana

Assume that the TiDB cluster topology is as follows:

| Name  | Host IP | Services |
| :-- | :-- | :-------------- |
| Node1 | 192.168.199.113| PD1, TiDB, node_export, Prometheus, Grafana |
| Node2 | 192.168.199.114| PD2, node_export  |
| Node3 | 192.168.199.115| PD3, node_export |
| Node4 | 192.168.199.116| TiKV1, node_export |
| Node5 | 192.168.199.117| TiKV2, node_export |
| Node6 | 192.168.199.118| TiKV3, node_export |
### Step 1: Download the binary package

```bash
# Downloads the package.
wget https://github.com/prometheus/prometheus/releases/download/v2.49.1/prometheus-2.49.1.linux-amd64.tar.gz
wget https://download.pingcap.com/node_exporter-v1.3.1-linux-amd64.tar.gz
wget https://download.pingcap.com/grafana-7.5.17.linux-amd64.tar.gz
```

```bash
# Extracts the package.
tar -xzf prometheus-2.49.1.linux-amd64.tar.gz
tar -xzf node_exporter-v1.3.1-linux-amd64.tar.gz
tar -xzf grafana-7.5.17.linux-amd64.tar.gz
```
### Step 2: Start `node_exporter` on Node1, Node2, Node3, and Node4

```bash
cd node_exporter-v1.3.1-linux-amd64

# Starts the node_exporter service.
$ ./node_exporter --web.listen-address=":9100" \
    --log.level="info" &
```
### Step 3: Start Prometheus on Node1

Edit the Prometheus configuration file:

```bash
cd prometheus-2.49.1.linux-amd64 &&
vi prometheus.yml
```

```ini
...

global:
  scrape_interval:     15s  # By default, scrape targets every 15 seconds.
  evaluation_interval: 15s  # By default, scrape targets every 15 seconds.
  # scrape_timeout is set to the global default value (10s).
  external_labels:
    cluster: 'test-cluster'
    monitor: "prometheus"

scrape_configs:
  - job_name: 'overwritten-nodes'
    honor_labels: true  # Do not overwrite job & instance labels.
    static_configs:
    - targets:
      - '192.168.199.113:9100'
      - '192.168.199.114:9100'
      - '192.168.199.115:9100'
      - '192.168.199.116:9100'
      - '192.168.199.117:9100'
      - '192.168.199.118:9100'

  - job_name: 'tidb'
    honor_labels: true  # Do not overwrite job & instance labels.
    static_configs:
    - targets:
      - '192.168.199.113:10080'

  - job_name: 'pd'
    honor_labels: true  # Do not overwrite job & instance labels.
    static_configs:
    - targets:
      - '192.168.199.113:2379'
      - '192.168.199.114:2379'
      - '192.168.199.115:2379'

  - job_name: 'tikv'
    honor_labels: true  # Do not overwrite job & instance labels.
    static_configs:
    - targets:
      - '192.168.199.116:20180'
      - '192.168.199.117:20180'
      - '192.168.199.118:20180'

...
```

To enable alarm rules for components such as TiDB, PD, and TiKV, download the alarm rule files of the corresponding components separately, and then add the configurations of alarm rule files to the Prometheus configuration file.

- TiDB: [`tidb.rules.yml`](https://github.com/pingcap/tidb/blob/master/pkg/metrics/alertmanager/tidb.rules.yml)
- PD: [`pd.rules.yml`](https://github.com/tikv/pd/blob/master/metrics/alertmanager/pd.rules.yml)
- TiKV: [`tikv.rules.yml`](https://github.com/tikv/tikv/blob/master/metrics/alertmanager/tikv.rules.yml)
- TiFlash: [`tiflash.rules.yml`](https://github.com/pingcap/tiflash/blob/master/metrics/alertmanager/tiflash.rules.yml)
- TiCDC: [`ticdc.rules.yml`](https://github.com/pingcap/tiflow/blob/master/metrics/alertmanager/ticdc.rules.yml)
- TiDB Lightning: [`lightning.rules.yml`](https://github.com/pingcap/tidb/blob/master/br/metrics/alertmanager/lightning.rules.yml)

```ini
rule_files:
  - 'tidb.rules.yml'
  - 'pd.rules.yml'
  - 'tikv.rules.yml'
  - 'tiflash.rules.yml'
  - 'ticdc.rules.yml'
  - 'lightning.rules.yml'
```

Start the Prometheus service:

```bash
$ ./prometheus \
    --config.file="./prometheus.yml" \
    --web.listen-address=":9090" \
    --web.external-url="http://192.168.199.113:9090/" \
    --web.enable-admin-api \
    --log.level="info" \
    --storage.tsdb.path="./data.metrics" \
    --storage.tsdb.retention="15d" &
```
### Step 4: Start Grafana on Node1

Edit the Grafana configuration file:

```ini
cd grafana-7.5.17 &&
vi conf/grafana.ini

...

[paths]
data = ./data
logs = ./data/log
plugins = ./data/plugins
[server]
http_port = 3000
domain = 192.168.199.113
[database]
[session]
[analytics]
check_for_updates = true
[security]
admin_user = admin
admin_password = admin
[snapshots]
[users]
[auth.anonymous]
[auth.basic]
[auth.ldap]
[smtp]
[emails]
[log]
mode = file
[log.console]
[log.file]
level = info
format = text
[log.syslog]
[event_publisher]
[dashboards.json]
enabled = false
path = ./data/dashboards
[metrics]
[grafana_net]
url = https://grafana.net

...

```

Start the Grafana service:

```bash
./bin/grafana-server \
    --config="./conf/grafana.ini" &
```
