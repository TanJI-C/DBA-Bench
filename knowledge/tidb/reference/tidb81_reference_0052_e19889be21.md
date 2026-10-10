# DM cluster diagnostic data types and log classification

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/clinic/clinic-data-instruction-for-tiup.md`
- Source Title: `PingCAP Clinic Diagnostic Data`
- Source Heading Path: `PingCAP Clinic Diagnostic Data > DM clusters | PingCAP Clinic Diagnostic Data > DM clusters > DM cluster information | PingCAP Clinic Diagnostic Data > DM clusters > dm-master diagnostic data | PingCAP Clinic Diagnostic Data > DM clusters > dm-worker diagnostic data | PingCAP Clinic Diagnostic Data > DM clusters > Prometheus monitoring data | PingCAP Clinic Diagnostic Data > DM clusters > System information of the cluster node | PingCAP Clinic Diagnostic Data > DM clusters > Log file classification`
- Source Line Ranges: `101-154`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `dm`, `shared`
- Topic Tags: `clinic`, `diagnostic-data`, `data-collection`, `cluster-information`, `logs`, `config`, `monitoring`, `system-information`, `log-classification`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0052_e19889be21`
- Source ID: `tidb-docs-8.1:clinic/clinic-data-instruction-for-tiup.md#dm-clusters`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b9ada68b0d8f761c063243457179e3c25f54eac82408357eea644638a04b4bfe`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/clinic/clinic-data-instruction-for-tiup#dm-clusters
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/clinic/clinic-data-instruction-for-tiup.md

## Retrieval Guidance

- Use When: Use this chunk when identifying which diagnostic data types Diag can collect from a DM cluster deployed using TiUP, including dm-master and dm-worker files, monitoring and system data, and log type classification with --include=log.<type>.
- Retrieval Keywords: DM clusters, Diag, DM cluster information, dm-master diagnostic data, dm-worker diagnostic data, Log file classification, --include=log, --include=config, --include=monitor, --include=system, --include=log.<type>, cluster.json, meta.yaml, dm-master.log, dm-master_stderr.log, dm-master.toml, dm-worker.log, dm-worker_stderr.log, dm-work.toml, {metric_name}.json, alerts.json, dmesg.log, insight.json, limits.conf, sysctl.conf, ss.txt, std, rocksdb, slow, unknown
- Follow-up Guidance: The source states that `--include=log.<type>` supports `std` for filenames containing `stderr`, `rocksdb` for files with a `rocksdb` prefix and a `.info` suffix, `slow` for slow query log files, and `unknown` for files that match none of these types.
- Classification Note: This is reference content because it lists DM diagnostic data, exported files, collection parameters, and the defined log type categories for selective log collection.

## Official Source Content

## DM clusters

This section lists the types of diagnostic data that can be collected by Diag from the DM clusters deployed using TiUP.
### DM cluster information

| Data type | Exported file | Parameter for data collection by PingCAP Clinic |
| :------ | :------ |:-------- |
| Basic information of the cluster, including the cluster ID  | `cluster.json`| The data is collected per run by default. |
| Detailed information of the cluster | `meta.yaml` | The data is collected per run by default. |
### dm-master diagnostic data

| Data type | Exported file | Parameter for data collection by PingCAP Clinic |
| :------ | :------ |:-------- |
| Log | `dm-master.log` | `--include=log` |
| Error log | `dm-master_stderr.log` | `--include=log` |
| Configuration file | `dm-master.toml` | `--include=config` |
### dm-worker diagnostic data

| Data type | Exported file | Parameter for data collection by PingCAP Clinic |
| :------ | :------ |:-------- |
| Log| `dm-worker.log` | `--include=log`|
| Error log | `dm-worker_stderr.log` | `--include=log` |
| Configuration file | `dm-work.toml` | `--include=config` |
### Prometheus monitoring data

| Data type | Exported file | Parameter for data collection by PingCAP Clinic |
| :------ | :------ |:-------- |
| All metrics data | `{metric_name}.json` | `--include=monitor` |
| All alerts data | `alerts.json` | `--include=monitor` |
### System information of the cluster node

| Data type | Exported file | Parameter for data collection by PingCAP Clinic |
| :------ | :------ |:-------- |
| Kernel log | `dmesg.log` | `--include=system` |
| Basic information of the system and hardware | `insight.json` | `--include=system` |
| Contents in the `/etc/security/limits.conf` system | `limits.conf` | `--include=system` |
| List of kernel parameters | `sysctl.conf` | `--include=system` |
| Socket system information, which is the output of the `ss` command | `ss.txt` | `--include=system` |
### Log file classification

You can use the `--include=log.<type>` parameter to specify which types of logs to collect.

Log types:

- `std`: Log files that contain `stderr` in the filename.
- `rocksdb`: Log files with a `rocksdb` prefix and a `.info` suffix.
- `slow`: Slow query log files.
- `unknown`: Log files that do not match any of the preceding types.
