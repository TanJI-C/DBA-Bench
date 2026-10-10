# TiCDC server CLI parameters

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-server-config.md`
- Source Title: `TiCDC Server Configurations`
- Source Heading Path: `TiCDC Server Configurations | TiCDC Server Configurations > `cdc server` CLI parameters`
- Source Line Ranges: `5-28`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `pd`, `tiup`
- Topic Tags: `cli`, `server`, `parameters`, `networking`, `tls`, `logging`, `storage`, `gc-safepoint`, `timezone`, `cluster-id`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0181_630b0cda70`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-server-config.md#ticdc-server-configurations`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ecae67a39e8b82b4622e36599910449b5ea2c7486bd46d9f92d088b868ceb10d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-server-config#ticdc-server-configurations
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-server-config.md

## Retrieval Guidance

- Use When: Use this chunk when looking up `cdc server` CLI parameters for TiCDC server startup, networking, TLS, logging, storage, GC safepoint TTL, time zone, or cluster identification.
- Retrieval Keywords: cdc server CLI parameters, addr, advertise-addr, pd, config, data-dir, gc-ttl, GC safepoint, log-file, log-level, ca, cert, cert-allowed-cn, key, tz, time-zone in sink-uri, cluster-id, 127.0.0.1:8300, default
- Follow-up Guidance: The `config` option points to the TiCDC server configuration file, and the `tz` description references `time-zone` in `sink-uri` and the Complete Behavior of TiCDC GC safepoint FAQ.
- Classification Note: This is configuration content because it enumerates TiCDC `cdc server` command-line options and their meanings, defaults, and constraints.

## Official Source Content

# TiCDC Server Configurations

This document describes the CLI and configuration file parameters used in TiCDC.
## `cdc server` CLI parameters

The following are descriptions of options available in a `cdc server` command:

- `addr`: The listening address of TiCDC, the HTTP API address, and the Prometheus address of the TiCDC service. The default value is `127.0.0.1:8300`.
- `advertise-addr`: The advertised address via which clients access TiCDC. If unspecified, the value is the same as that of `addr`.
- `pd`: A comma-separated list of PD endpoints.
- `config`: The address of the configuration file that TiCDC uses (optional). This option is supported since TiCDC v5.0.0. This option can be used in the TiCDC deployment since TiUP v1.4.0. For detailed configuration description, see [TiCDC Changefeed Configurations](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config)
- `data-dir`: Specifies the directory that TiCDC uses when it needs to use disks to store files. The sort engine used by TiCDC and redo logs use this directory to store temporary files. It is recommended to ensure that the free disk space for this directory is greater than or equal to 500 GiB. If you are using TiUP, you can configure `data_dir` in the [`cdc_servers`](https://docs.pingcap.com/tidb/stable/tiup/tiup-cluster-topology-reference#cdc_servers) section, or directly use the default `data_dir` path in `global`.
- `gc-ttl`: The TTL (Time To Live) of the service level `GC safepoint` in PD set by TiCDC, and the duration that the replication task can suspend, in seconds. The default value is `86400`, which means 24 hours. Note: Suspending of the TiCDC replication task affects the progress of TiCDC GC safepoint, which means that it affects the progress of upstream TiDB GC, as detailed in [Complete Behavior of TiCDC GC safepoint](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-faq#what-is-the-complete-behavior-of-ticdc-garbage-collection-gc-safepoint).
- `log-file`: The path to which logs are output when the TiCDC process is running. If this parameter is not specified, logs are written to the standard output (stdout).
- `log-level`: The log level when the TiCDC process is running. The default value is `"info"`.
- `ca`: Specifies the path of the CA certificate file in PEM format for TLS connection (optional).
- `cert`: Specifies the path of the certificate file in PEM format for TLS connection (optional).
- `cert-allowed-cn`: Specifies the path of the common name in PEM format for TLS connection (optional).
- `key`: Specifies the path of the private key file in PEM format for TLS connection (optional).
- `tz`: Time zone used by the TiCDC service. TiCDC uses this time zone when it internally converts time data types such as `TIMESTAMP` or when it replicates data to the downstream. The default is the local time zone in which the process runs. If you specify `time-zone` (in `sink-uri`) and `tz` at the same time, the internal TiCDC processes use the time zone specified by `tz`, and the sink uses the time zone specified by `time-zone` for replicating data to the downstream. Make sure that the time zone specified by `tz` is the same as that specified by `time-zone` (in `sink-uri`).
- `cluster-id`: (optional) The ID of the TiCDC cluster. The default value is `default`. `cluster-id` is the unique identifier of a TiCDC cluster. TiCDC nodes with the same `cluster-id` belong to the same cluster. The length of a `cluster-id` is 128 characters at most. `cluster-id` must follow the pattern of `^[a-zA-Z0-9]+(-[a-zA-Z0-9]+)*$` and cannot be one of the following: `owner`, `capture`, `task`, `changefeed`, `job`, and `meta`.
