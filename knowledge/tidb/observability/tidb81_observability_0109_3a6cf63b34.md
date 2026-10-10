# TiDB Lightning monitoring setup and Grafana dashboard panels

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-lightning/monitor-tidb-lightning.md`
- Source Title: `TiDB Lightning Monitoring`
- Source Heading Path: `TiDB Lightning Monitoring | TiDB Lightning Monitoring > Monitor configuration | TiDB Lightning Monitoring > Grafana dashboard | TiDB Lightning Monitoring > Grafana dashboard > Row 1: Speed | TiDB Lightning Monitoring > Grafana dashboard > Row 2: Progress | TiDB Lightning Monitoring > Grafana dashboard > Row 3: Resource | TiDB Lightning Monitoring > Grafana dashboard > Row 4: Quota | TiDB Lightning Monitoring > Grafana dashboard > Row 5: Read speed | TiDB Lightning Monitoring > Grafana dashboard > Row 6: Storage | TiDB Lightning Monitoring > Grafana dashboard > Row 7: Import speed`
- Source Line Ranges: `5-123`
- Source Scope: `self_managed`
- Primary Component: `lightning`
- Related Components: `shared`, `tikv`
- Topic Tags: `prometheus`, `grafana`, `metrics`, `dashboard`, `monitoring`, `import-speed`, `progress`, `resource-usage`, `quota`, `read-speed`, `storage`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0109_3a6cf63b34`
- Source ID: `tidb-docs-8.1:tidb-lightning/monitor-tidb-lightning.md#tidb-lightning-monitoring`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6a79abb186be511c3acd1ac4a4710292b890d06b2fa1c3ec188a32d6fb4dfbbf`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-lightning/monitor-tidb-lightning#tidb-lightning-monitoring
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-lightning/monitor-tidb-lightning.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs TiDB Lightning monitoring setup details or wants to interpret Grafana dashboard panels for speed, progress, resource, quota, read speed, storage, and import speed.
- Retrieval Keywords: tidb-lightning Prometheus metrics, pprof-port = 8289, scrape_configs, job_name: 'tidb-lightning', Grafana dashboard, Import speed, write from TiDB Lightning, upload to tikv, Chunk process duration, Import progress, Checksum progress, Failures, Memory usage, Number of TiDB Lightning Goroutines, CPU%, Idle workers, io-concurrency, closed-engine, table-concurrency, index-concurrency, region-concurrency, KV Encoder, Importer Engines, max-open-engines, Chunk parser read block duration, apply worker, SQL process duration, row encode, block deliver, SQL process rate, data deliver rate, index deliver rate, total deliver rate, parser read size, storage_size / 3, Delivery duration, Range delivery, SST delivery, SST process duration, Split SST, SST upload, SST ingest, SST size
- Follow-up Guidance: The source also provides metric collection setup through Prometheus discovery and a metrics port configured in tidb-lightning.toml.
- Classification Note: This is classified as observability because the content explains Prometheus collection and Grafana panels used to monitor TiDB Lightning behavior and resource usage.

## Official Source Content

# TiDB Lightning Monitoring

`tidb-lightning` supports metrics collection via [Prometheus](https://prometheus.io/). This document introduces the monitor configuration and monitoring metrics of TiDB Lightning.
## Monitor configuration

If TiDB Lightning is manually installed, follow the instructions below.

The metrics of `tidb-lightning` can be gathered directly by Prometheus as long as it is discovered. You can set the metrics port in `tidb-lightning.toml`:

```toml
[lightning]
# HTTP port for debugging and Prometheus metrics pulling (0 to disable)
pprof-port = 8289

...
```

You need to configure Prometheus to make it discover the servers. For instance, you can directly add the server address to the `scrape_configs` section:

```yaml
...
scrape_configs:
  - job_name: 'tidb-lightning'
    static_configs:
      - targets: ['192.168.20.10:8289']
```
## Grafana dashboard

[Grafana](https://grafana.com/) is a web interface to visualize Prometheus metrics as dashboards.
### Row 1: Speed

![Panels in first row](/media/lightning-grafana-row-1.png)

| Panel | Series | Description |
|:-----|:-----|:-----|
| Import speed | write from TiDB Lightning | Speed of sending KVs from TiDB Lightning to TiKV Importer, which depends on each table's complexity |
| Import speed | upload to tikv | Total upload speed from TiKV Importer to all TiKV replicas |
| Chunk process duration | | Average time needed to completely encode one single data file |

Sometimes the import speed will drop to zero allowing other parts to catch up. This is normal.
### Row 2: Progress

![Panels in second row](/media/lightning-grafana-row-2.png)

| Panel | Description |
|:-----|:-----|
| Import progress | Percentage of data files encoded so far |
| Checksum progress | Percentage of tables are verified to be imported successfully |
| Failures | Number of failed tables and their point of failure, normally empty |
### Row 3: Resource

![Panels in third row](/media/lightning-grafana-row-3.png)

| Panel | Description |
|:-----|:-----|
| Memory usage | Amount of memory occupied by each service |
| Number of TiDB Lightning Goroutines | Number of running goroutines used by TiDB Lightning |
| CPU% | Number of logical CPU cores utilized by each service |
### Row 4: Quota

![Panels in fourth row](/media/lightning-grafana-row-4.png)

| Panel | Series | Description |
|:-----|:-----|:-----|
| Idle workers | io | Number of unused `io-concurrency`, normally close to configured value (default 5), and close to 0 means the disk is too slow |
| Idle workers | closed-engine | Number of engines which is closed but not yet cleaned up, normally close to index + table-concurrency (default 8), and close to 0 means TiDB Lightning is faster than TiKV Importer, which will cause TiDB Lightning to stall |
| Idle workers | table | Number of unused `table-concurrency`, normally 0 until the end of process |
| Idle workers | index | Number of unused `index-concurrency`, normally 0 until the end of process |
| Idle workers | region | Number of unused `region-concurrency`, normally 0 until the end of process |
| External resources | KV Encoder | Counts active KV encoders, normally the same as `region-concurrency` until the end of process |
| External resources | Importer Engines | Counts opened engine files, should never exceed the `max-open-engines` setting |
### Row 5: Read speed

![Panels in fifth row](/media/lightning-grafana-row-5.png)

| Panel | Series | Description |
|:-----|:-----|:-----|
| Chunk parser read block duration | read block | Time taken to read one block of bytes to prepare for parsing |
| Chunk parser read block duration | apply worker | Time elapsed to wait for an idle io-concurrency |
| SQL process duration | row encode | Time taken to parse and encode a single row |
| SQL process duration | block deliver | Time taken to send a block of KV pairs to TiKV Importer |

If any of the duration is too high, it indicates that the disk used by TiDB Lightning is too slow or busy with I/O.
### Row 6: Storage

![Panels in sixth row](/media/lightning-grafana-row-6.png)

| Panel | Series | Description |
|:-----|:-----|:-----|
| SQL process rate | data deliver rate | Speed of delivery of data KV pairs to TiKV Importer |
| SQL process rate | index deliver rate | Speed of delivery of index KV pairs to TiKV Importer |
| SQL process rate | total deliver rate | The sum of two rates above |
| Total bytes | parser read size | Number of bytes being read by TiDB Lightning |
| Total bytes | data deliver size | Number of bytes of data KV pairs already delivered to TiKV Importer |
| Total bytes | index deliver size | Number of bytes of index KV pairs already delivered to TiKV Importer |
| Total bytes | storage_size / 3 | Total size occupied by the TiKV cluster, divided by 3 (the default number of replicas) |
### Row 7: Import speed

![Panels in seventh row](/media/lightning-grafana-row-7.png)

| Panel | Series | Description |
|:-----|:-----|:-----|
| Delivery duration | Range delivery | Time taken to upload a range of KV pairs to the TiKV cluster |
| Delivery duration | SST delivery | Time taken to upload an SST file to the TiKV cluster |
| SST process duration | Split SST | Time taken to split the stream of KV pairs into SST files |
| SST process duration | SST upload | Time taken to upload an SST file |
| SST process duration | SST ingest | Time taken to ingest an uploaded SST file |
| SST process duration | SST size | File size of an SST file |
