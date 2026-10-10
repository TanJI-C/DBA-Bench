# Blackbox exporter service availability and ping alerts

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/alert-rules.md`
- Source Title: `TiDB Cluster Alert Rules`
- Source Heading Path: `TiDB Cluster Alert Rules > Blackbox_exporter TCP, ICMP, and HTTP alert rules | TiDB Cluster Alert Rules > Blackbox_exporter TCP, ICMP, and HTTP alert rules > Emergency-level alerts | TiDB Cluster Alert Rules > Blackbox_exporter TCP, ICMP, and HTTP alert rules > Emergency-level alerts > `TiDB_server_is_down` | TiDB Cluster Alert Rules > Blackbox_exporter TCP, ICMP, and HTTP alert rules > Emergency-level alerts > `TiFlash_server_is_down` | TiDB Cluster Alert Rules > Blackbox_exporter TCP, ICMP, and HTTP alert rules > Emergency-level alerts > `Pump_server_is_down` | TiDB Cluster Alert Rules > Blackbox_exporter TCP, ICMP, and HTTP alert rules > Emergency-level alerts > `Drainer_server_is_down` | TiDB Cluster Alert Rules > Blackbox_exporter TCP, ICMP, and HTTP alert rules > Emergency-level alerts > `TiKV_server_is_down` | TiDB Cluster Alert Rules > Blackbox_exporter TCP, ICMP, and HTTP alert rules > Emergency-level alerts > `PD_server_is_down` | TiDB Cluster Alert Rules > Blackbox_exporter TCP, ICMP, and HTTP alert rules > Emergency-level alerts > `Node_exporter_server_is_down` | TiDB Cluster Alert Rules > Blackbox_exporter TCP, ICMP, and HTTP alert rules > Emergency-level alerts > `Blackbox_exporter_server_is_down` | TiDB Cluster Alert Rules > Blackbox_exporter TCP, ICMP, and HTTP alert rules > Emergency-level alerts > `Grafana_server_is_down` | TiDB Cluster Alert Rules > Blackbox_exporter TCP, ICMP, and HTTP alert rules > Emergency-level alerts > `Pushgateway_server_is_down` | TiDB Cluster Alert Rules > Blackbox_exporter TCP, ICMP, and HTTP alert rules > Emergency-level alerts > `Kafka_exporter_is_down` | TiDB Cluster Alert Rules > Blackbox_exporter TCP, ICMP, and HTTP alert rules > Emergency-level alerts > `Pushgateway_metrics_interface` | TiDB Cluster Alert Rules > Blackbox_exporter TCP, ICMP, and HTTP alert rules > Warning-level alerts | TiDB Cluster Alert Rules > Blackbox_exporter TCP, ICMP, and HTTP alert rules > Warning-level alerts > `BLACKER_ping_latency_more_than_1s``
- Source Line Ranges: `933-1146`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `tiflash`
- Topic Tags: `alert-rules`, `blackbox-exporter`, `service-probing`, `availability`, `icmp`, `http`, `tcp`, `ping-latency`, `grafana`, `network`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0008_d4b53b6c79`
- Source ID: `tidb-docs-8.1:alert-rules.md#blackbox-exporter-tcp-icmp-and-http-alert-rules`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b18517770bc56c75bd434f72c00692bf5dab66d34e98e50d9cefd6fd657069da`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/alert-rules#blackbox-exporter-tcp-icmp-and-http-alert-rules
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/alert-rules.md

## Retrieval Guidance

- Use When: Use this chunk when an alert or search concerns Blackbox_exporter TCP, ICMP, or HTTP probing failures, service down alerts for TiDB ecosystem components, or ping latency above 1 second.
- Retrieval Keywords: Blackbox_exporter TCP, ICMP, and HTTP alert rules, TiDB_server_is_down, TiFlash_server_is_down, Pump_server_is_down, Drainer_server_is_down, TiKV_server_is_down, PD_server_is_down, Node_exporter_server_is_down, Blackbox_exporter_server_is_down, Grafana_server_is_down, Pushgateway_server_is_down, Kafka_exporter_is_down, Pushgateway_metrics_interface, BLACKER_ping_latency_more_than_1s, probe_success, probe_duration_seconds, blackbox_exporter_http, blackbox_exporter.*_icmp, Failure to probe the TiDB service port, Failure to probe the Pushgateway service http interface, ping latency exceeds 1 second
- Follow-up Guidance: The source says to check whether the relevant machine is down, whether the related process exists, whether the network between the monitoring machine and that machine is normal, and for ping latency to view the Grafana Blackbox Exporter page and the TCP panel on the Grafana Node Exporter page.
- Classification Note: The official content classifies these as Blackbox_exporter emergency-level service availability alerts and one warning-level ping latency alert.

## Official Source Content

## Blackbox_exporter TCP, ICMP, and HTTP alert rules

This section gives the alert rules for the Blackbox_exporter TCP, ICMP, and HTTP.
### Emergency-level alerts
#### `TiDB_server_is_down`

* Alert rule:

    `probe_success{group="tidb"} == 0`

* Description:

    Failure to probe the TiDB service port.

* Solution:

    * Check whether the machine that provides the TiDB service is down.
    * Check whether the TiDB process exists.
    * Check whether the network between the monitoring machine and the TiDB machine is normal.
#### `TiFlash_server_is_down`

* Alert rule:

    `probe_success{group="tiflash"} == 0`

* Description:

    Failure to probe the TiFlash service port.

* Solution:

    * Check whether the machine that provides the TiFlash service is down.
    * Check whether the TiFlash process exists.
    * Check whether the network between the monitoring machine and the TiFlash machine is normal.
#### `Pump_server_is_down`

* Alert rule:

    `probe_success{group="pump"} == 0`

* Description:

    Failure to probe the pump service port.

* Solution:

    * Check whether the machine that provides the pump service is down.
    * Check whether the pump process exists.
    * Check whether the network between the monitoring machine and the pump machine is normal.
#### `Drainer_server_is_down`

* Alert rule:

    `probe_success{group="drainer"} == 0`

* Description:

    Failure to probe the Drainer service port.

* Solution:

    * Check whether the machine that provides the Drainer service is down.
    * Check whether the Drainer process exists.
    * Check whether the network between the monitoring machine and the Drainer machine is normal.
#### `TiKV_server_is_down`

* Alert rule:

    `probe_success{group="tikv"} == 0`

* Description:

    Failure to probe the TiKV service port.

* Solution:

    * Check whether the machine that provides the TiKV service is down.
    * Check whether the TiKV process exists.
    * Check whether the network between the monitoring machine and the TiKV machine is normal.
#### `PD_server_is_down`

* Alert rule:

    `probe_success{group="pd"} == 0`

* Description:

    Failure to probe the PD service port.

* Solution:

    * Check whether the machine that provides the PD service is down.
    * Check whether the PD process exists.
    * Check whether the network between the monitoring machine and the PD machine is normal.
#### `Node_exporter_server_is_down`

* Alert rule:

    `probe_success{group="node_exporter"} == 0`

* Description:

    Failure to probe the Node_exporter service port.

* Solution:

    * Check whether the machine that provides the Node_exporter service is down.
    * Check whether the Node_exporter process exists.
    * Check whether the network between the monitoring machine and the Node_exporter machine is normal.
#### `Blackbox_exporter_server_is_down`

* Alert rule:

    `probe_success{group="blackbox_exporter"} == 0`

* Description:

    Failure to probe the Blackbox_Exporter service port.

* Solution:

    * Check whether the machine that provides the Blackbox_Exporter service is down.
    * Check whether the Blackbox_Exporter process exists.
    * Check whether the network between the monitoring machine and the Blackbox_Exporter machine is normal.
#### `Grafana_server_is_down`

* Alert rule:

    `probe_success{group="grafana"} == 0`

* Description:

    Failure to probe the Grafana service port.

* Solution:

    * Check whether the machine that provides the Grafana service is down.
    * Check whether the Grafana process exists.
    * Check whether the network between the monitoring machine and the Grafana machine is normal.
#### `Pushgateway_server_is_down`

* Alert rule:

    `probe_success{group="pushgateway"} == 0`

* Description:

    Failure to probe the Pushgateway service port.

* Solution:

    * Check whether the machine that provides the Pushgateway service is down.
    * Check whether the Pushgateway process exists.
    * Check whether the network between the monitoring machine and the Pushgateway machine is normal.
#### `Kafka_exporter_is_down`

* Alert rule:

    `probe_success{group="kafka_exporter"} == 0`

* Description:

    Failure to probe the Kafka_Exporter service port.

* Solution:

    * Check whether the machine that provides the Kafka_Exporter service is down.
    * Check whether the Kafka_Exporter process exists.
    * Check whether the network between the monitoring machine and the Kafka_Exporter machine is normal.
#### `Pushgateway_metrics_interface`

* Alert rule:

    `probe_success{job="blackbox_exporter_http"} == 0`

* Description:

    Failure to probe the Pushgateway service http interface.

* Solution:

    * Check whether the machine that provides the Pushgateway service is down.
    * Check whether the Pushgateway process exists.
    * Check whether the network between the monitoring machine and the Pushgateway machine is normal.
### Warning-level alerts
#### `BLACKER_ping_latency_more_than_1s`

* Alert rule:

    `max_over_time(probe_duration_seconds{job=~"blackbox_exporter.*_icmp"}[1m]) > 1`

* Description:

    The ping latency exceeds 1 second.

* Solution:

    * View the ping latency between the two nodes on the Grafana Blackbox Exporter page to check whether it is too high.
    * Check the TCP panel on the Grafana Node Exporter page to check whether there is any packet loss.
