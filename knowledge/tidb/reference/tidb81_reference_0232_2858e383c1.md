# DM-worker configuration template and global parameters

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-worker-configuration-file.md`
- Source Title: `DM-worker Configuration File`
- Source Heading Path: `DM-worker Configuration File | DM-worker Configuration File > Configuration file template | DM-worker Configuration File > Configuration parameters | DM-worker Configuration File > Configuration parameters > Global`
- Source Line Ranges: `5-55`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: none
- Topic Tags: `configuration`, `template`, `global parameters`, `ssl`, `relay log`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0232_2858e383c1`
- Source ID: `tidb-docs-8.1:dm/dm-worker-configuration-file.md#dm-worker-configuration-file`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `69140e88c1237ef043c9e6d92e533b51e0729d54f3bcac915c9669e5cdd5edc5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-worker-configuration-file#dm-worker-configuration-file
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-worker-configuration-file.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the DM-worker configuration file template or the meaning of global parameters such as listen addresses, join settings, keepalive TTL, relay log directory, and SSL options.
- Retrieval Keywords: DM-worker Configuration File, configuration file template, name, log-level, log-file, worker-addr, advertise-addr, join, keepalive-ttl, relay-keepalive-ttl, relay-dir, ssl-ca, ssl-cert, ssl-key, cert-allowed-cn, master-addr, relay log, Global
- Follow-up Guidance: The source states that `join` corresponds to one or more `master-addr`s in the DM-master configuration file.
- Classification Note: This is reference content because it provides a DM-worker configuration template and a parameter-by-parameter description of global configuration fields.

## Official Source Content

# DM-worker Configuration File

This document introduces the configuration of DM worker, including a configuration file template and a description of each configuration parameter in this file.
## Configuration file template

The following is a configuration file template of the DM-worker:

```toml
# Worker Configuration.
name = "worker1"

# Log configuration.
log-level = "info"
log-file = "dm-worker.log"

# DM-worker listen address.
worker-addr = ":8262"
advertise-addr = "127.0.0.1:8262"
join = "http://127.0.0.1:8261,http://127.0.0.1:8361,http://127.0.0.1:8461"

keepalive-ttl = 60
relay-keepalive-ttl = 1800 # New in DM v2.0.2.
# relay-dir = "relay_log" # New in 5.4.0. When you use a relative path, check the deployment and start method of DM-worker to determine the full path.

ssl-ca = "/path/to/ca.pem"
ssl-cert = "/path/to/cert.pem"
ssl-key = "/path/to/key.pem"
cert-allowed-cn = ["dm"]
```
## Configuration parameters
### Global

| Parameter        | Description                           |
| :------------ | :--------------------------------------- |
| `name` | The name of the DM-worker. |
| `log-level` | Specifies a log level from `debug`, `info`, `warn`, `error`, and `fatal`. The default log level is `info`. |
| `log-file` | Specifies the log file directory. If this parameter is not specified, the logs are printed onto the standard output. |
| `worker-addr` | Specifies the address of DM-worker which provides services. You can omit the IP address and specify the port number only, such as ":8262". |
| `advertise-addr` | Specifies the address that DM-worker advertises to the outside world. |
| `join` | Corresponds to one or more [`master-addr`s](https://docs.pingcap.com/tidb/stable/dm/dm-master-configuration-file#global-configuration) in the DM-master configuration file. |
| `keepalive-ttl` | The keepalive time (in seconds) of a DM-worker node to the DM-master node if the upstream data source of the DM-worker node does not enable the relay log. The default value is 60s.|
| `relay-keepalive-ttl` | The keepalive time (in seconds) of a DM-worker node to the DM-master node if the upstream data source of the DM-worker node enables the relay log. The default value is 1800s. This parameter is added since DM v2.0.2.|
| `relay-dir` | When relay log is enabled in the bound upstream data source, DM-worker stores the relay log in this directory. This parameter is new in v5.4.0 and takes precedence over the configuration of the upstream data source. |
| `ssl-ca` | The path of the file that contains list of trusted SSL CAs for DM-worker to connect with other components. |
| `ssl-cert` | The path of the file that contains X509 certificate in PEM format for DM-worker to connect with other components. |
| `ssl-key` | The path of the file that contains X509 key in PEM format for DM-worker to connect with other components. |
| `cert-allowed-cn` | Common Name list. |
