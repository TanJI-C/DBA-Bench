# TiKV backup and encryption metrics

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/grafana-tikv-dashboard.md`
- Source Title: `Key Monitoring Metrics of TiKV`
- Source Heading Path: `Key Monitoring Metrics of TiKV > TiKV-Details dashboard > Backup | Key Monitoring Metrics of TiKV > TiKV-Details dashboard > Encryption`
- Source Line Ranges: `442-460`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `br`
- Topic Tags: `grafana`, `metrics`, `backup`, `encryption`, `cpu`, `throughput`, `errors`, `keys`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0063_8ed62ae672`
- Source ID: `tidb-docs-8.1:grafana-tikv-dashboard.md#backup`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `02f7fa388bad4baf613ab56d32d38ebb4856c49d81f9ca079745940661e122f3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/grafana-tikv-dashboard#backup
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/grafana-tikv-dashboard.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiKV-Details Grafana metrics for TiKV backup activity or encryption status and related durations, throughput, errors, and key counts.
- Retrieval Keywords: TiKV-Details dashboard, Backup, Encryption, Backup CPU, Range Size, Backup Duration, Backup Flow, Disk Throughput, Backup Range Duration, Backup Errors, Encryption data keys, Encrypted files, Encryption initialized, Encryption meta files size, Encrypt/decrypt data nanos, Read/write encryption meta duration
- Follow-up Guidance: The source states that Encryption initialized shows whether encryption is enabled, and 1 means enabled.
- Classification Note: The official content classifies these as observability metrics for TiKV backup and encryption on the TiKV-Details dashboard, including CPU, range, duration, throughput, error, and encryption key or file measurements.

## Official Source Content

### Backup

- Backup CPU: The CPU utilization of the backup thread
- Range Size: The histogram of backup range size
- Backup Duration: The time consumed for backup
- Backup Flow: The total bytes of backup
- Disk Throughput: The disk throughput per instance
- Backup Range Duration: The time consumed for backing up a range
- Backup Errors: The number of errors encountered during a backup
### Encryption

- Encryption data keys: The total number of encrypted data keys
- Encrypted files: The number of encrypted files
- Encryption initialized: Shows whether encryption is enabled. `1` means enabled.
- Encryption meta files size: The size of the encryption meta file
- Encrypt/decrypt data nanos: The histogram of duration on encrypting/decrypting data each time
- Read/write encryption meta duration: The time consumed for reading/writing encryption meta files
