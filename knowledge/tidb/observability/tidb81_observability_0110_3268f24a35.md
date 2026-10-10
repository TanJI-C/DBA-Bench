# TiDB monitoring status and metrics interfaces

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-monitoring-api.md`
- Source Title: `TiDB Monitoring API`
- Source Heading Path: `TiDB Monitoring API | TiDB Monitoring API > Use the status interface | TiDB Monitoring API > Use the status interface > TiDB server | TiDB Monitoring API > Use the status interface > Running status | TiDB Monitoring API > Use the status interface > Running status > Storage information | TiDB Monitoring API > Use the status interface > PD server | TiDB Monitoring API > Use the metrics interface`
- Source Line Ranges: `5-123`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `pd`, `tikv`
- Topic Tags: `monitoring`, `status-api`, `metrics`, `prometheus`, `grafana`, `health-check`, `storage-information`, `pd-api`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0110_3268f24a35`
- Source ID: `tidb-docs-8.1:tidb-monitoring-api.md#tidb-monitoring-api`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1aa13349a59ec93be661f9e5b5a8e9315b2ca08774ab1e4fea4ff980d56fad10`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-monitoring-api#tidb-monitoring-api
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-monitoring-api.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB cluster monitoring interfaces, including the TiDB status HTTP endpoints, PD API endpoint pattern, or the metrics interface based on Prometheus and Grafana.
- Retrieval Keywords: TiDB Monitoring API, status interface, metrics interface, http://${host}:${port}/status, http://${host}:${port}/schema_storage/${db}/${table}, http://${host}:${port}/schema_storage/test, TiDB API address, default port 10080, PD API address, http://${host}:${port}/pd/api/v1/${api_name}, default port 2379, /pd/api/v1/stores, Keepalive messages, running status, storage information, Prometheus, Grafana, connections, version, git_hash, table_schema, table_name, table_rows, capacity, available, leader_count, region_count, last_heartbeat_ts
- Follow-up Guidance: For PD API names, the source points to the PD API doc, and for the metrics interface it notes deploying Prometheus and Grafana and then configuring Grafana.
- Classification Note: This is classified as observability because the content describes monitoring APIs for component status, TiKV cluster details from PD, and cluster metrics viewed through Prometheus and Grafana.

## Official Source Content

# TiDB Monitoring API

You can use the following types of interfaces to monitor the TiDB cluster status:

- [The status interface](#use-the-status-interface): this interface uses the HTTP interface to get the component information. Using this interface, you can get the [running status](#running-status) of the current TiDB server and the [storage information](#storage-information) of a table.
- [The metrics interface](#use-the-metrics-interface): this interface uses Prometheus to record the detailed information of the various operations in components and views these metrics using Grafana.
## Use the status interface

The status interface monitors the basic information of a specific component in the TiDB cluster. It can also act as the monitor interface for Keepalive messages. In addition, the status interface for the Placement Driver (PD) can get the details of the entire TiKV cluster.
### TiDB server

- TiDB API address: `http://${host}:${port}`
- Default port: `10080`
### Running status

The following example uses `http://${host}:${port}/status` to get the current status of the TiDB server and to determine whether the server is alive. The result is returned in **JSON** format.

```bash
curl http://127.0.0.1:10080/status
{
    connections: 0,  # The current number of clients connected to the TiDB server.
    version: "8.0.11-TiDB-v8.1.2",  # The TiDB version number.
    git_hash: "778c3f4a5a716880bcd1d71b257c8165685f0d70"  # The Git Hash of the current TiDB code.
}
```
#### Storage information

The following example uses `http://${host}:${port}/schema_storage/${db}/${table}` to get the storage information of the specific data table. The result is returned in **JSON** format.

```bash
curl http://127.0.0.1:10080/schema_storage/mysql/stats_histograms
```

```
{
    "table_schema": "mysql",
    "table_name": "stats_histograms",
    "table_rows": 0,
    "avg_row_length": 0,
    "data_length": 0,
    "max_data_length": 0,
    "index_length": 0,
    "data_free": 0
}
```

```bash
curl http://127.0.0.1:10080/schema_storage/test
```

```
[
    {
        "table_schema": "test",
        "table_name": "test",
        "table_rows": 0,
        "avg_row_length": 0,
        "data_length": 0,
        "max_data_length": 0,
        "index_length": 0,
        "data_free": 0
    }
]
```
### PD server

- PD API address: `http://${host}:${port}/pd/api/v1/${api_name}`
- Default port: `2379`
- Details about API names: see [PD API doc](https://docs-download.pingcap.com/api/pd-api/pd-api-v1.html)

The PD interface provides the status of all the TiKV servers and the information about load balancing. See the following example for the information about a single-node TiKV cluster:

```bash
curl http://127.0.0.1:2379/pd/api/v1/stores
{
  "count": 1,  # The number of TiKV nodes.
  "stores": [  # The list of TiKV nodes.
    # The details about the single TiKV node.
    {
      "store": {
        "id": 1,
        "address": "127.0.0.1:20160",
        "version": "3.0.0-beta",
        "state_name": "Up"
      },
      "status": {
        "capacity": "20 GiB",  # The total capacity.
        "available": "16 GiB",  # The available capacity.
        "leader_count": 17,
        "leader_weight": 1,
        "leader_score": 17,
        "leader_size": 17,
        "region_count": 17,
        "region_weight": 1,
        "region_score": 17,
        "region_size": 17,
        "start_ts": "2019-03-21T14:09:32+08:00",  # The starting timestamp.
        "last_heartbeat_ts": "2019-03-21T14:14:22.961171958+08:00",  # The timestamp of the last heartbeat.
        "uptime": "4m50.961171958s"
      }
    }
  ]
```
## Use the metrics interface

The metrics interface monitors the status and performance of the entire TiDB cluster.

- If you use other deployment ways, [deploy Prometheus and Grafana](https://docs.pingcap.com/tidb/stable/deploy-monitoring-services) before using this interface.

After Prometheus and Grafana are successfully deployed, [configure Grafana](https://docs.pingcap.com/tidb/stable/deploy-monitoring-services#configure-grafana).
