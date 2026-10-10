# Monitored service configuration

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-cluster-topology-reference.md`
- Source Title: `Topology Configuration File for TiDB Deployment Using TiUP`
- Source Heading Path: `Topology Configuration File for TiDB Deployment Using TiUP > File structure > `monitored``
- Source Line Ranges: `106-129`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `shared`
- Topic Tags: `monitoring`, `node-exporter`, `blackbox-exporter`, `ports`, `directories`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0398_03975637eb`
- Source ID: `tidb-docs-8.1:tiup/tiup-cluster-topology-reference.md#monitored`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `68b8028b690aa3eb1f06afdb9d09034f4524805114950847f40a8f8512991b3f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-cluster-topology-reference#monitored
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-cluster-topology-reference.md

## Retrieval Guidance

- Use When: Use this chunk when you need the `monitored` section settings for `node_exporter` and `blackbox_exporter`, especially their default ports and directory fields in a TiUP topology file.
- Retrieval Keywords: monitored section, node_exporter, blackbox_exporter, node_exporter_port, blackbox_exporter_port, 9100, 9115, monitored.deploy_dir, monitored.data_dir, monitored.log_dir, monitoring service on the target machine
- Follow-up Guidance: The chunk includes a `monitored` configuration example showing `node_exporter_port: 9100` and `blackbox_exporter_port: 9115`.
- Classification Note: This is configuration content because it specifies the fields and defaults for the monitored services section of the topology file.

## Official Source Content

### `monitored`

`monitored` is used to configure the monitoring service on the target machine: [`node_exporter`](https://github.com/prometheus/node_exporter) and [`blackbox_exporter`](https://github.com/prometheus/blackbox_exporter). The following fields are included:

- `node_exporter_port`: The service port of `node_exporter`. The default value is `9100`.

- `blackbox_exporter_port`: The service port of `blackbox_exporter`. The default value is `9115`.

- `deploy_dir`: Specifies the deployment directory. If it is not specified or specified as a relative directory, the directory is generated according to the `deploy_dir` directory configured in `global`.

- `data_dir`: Specifies the data directory. If it is not specified or specified as a relative directory, the directory is generated according to the `data_dir` directory configured in `global`.

- `log_dir`: Specifies the log directory. If it is not specified or specified as a relative directory, the log is generated according to the `log_dir` directory configured in `global`.

A `monitored` configuration example is as follows:

```yaml
monitored:
  node_exporter_port: 9100
  blackbox_exporter_port: 9115
```

The above configuration specifies that `node_exporter` uses the `9100` port and `blackbox_exporter` uses the `9115` port.
