# Pump configuration items

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-binlog/tidb-binlog-configuration-file.md`
- Source Title: `TiDB Binlog Configuration File`
- Source Heading Path: `TiDB Binlog Configuration File | TiDB Binlog Configuration File > Pump | TiDB Binlog Configuration File > Pump > addr | TiDB Binlog Configuration File > Pump > advertise-addr | TiDB Binlog Configuration File > Pump > socket | TiDB Binlog Configuration File > Pump > pd-urls | TiDB Binlog Configuration File > Pump > data-dir | TiDB Binlog Configuration File > Pump > heartbeat-interval | TiDB Binlog Configuration File > Pump > gen-binlog-interval | TiDB Binlog Configuration File > Pump > gc | TiDB Binlog Configuration File > Pump > log-file | TiDB Binlog Configuration File > Pump > log-level | TiDB Binlog Configuration File > Pump > node-id | TiDB Binlog Configuration File > Pump > security | TiDB Binlog Configuration File > Pump > security > ssl-ca | TiDB Binlog Configuration File > Pump > security > ssl-cert | TiDB Binlog Configuration File > Pump > security > ssl-key | TiDB Binlog Configuration File > Pump > storage | TiDB Binlog Configuration File > Pump > storage > sync-log | TiDB Binlog Configuration File > Pump > storage > kv_chan_cap | TiDB Binlog Configuration File > Pump > storage > slow_write_threshold | TiDB Binlog Configuration File > Pump > storage > stop-write-at-available-space | TiDB Binlog Configuration File > Pump > storage > kv`
- Source Line Ranges: `5-128`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `pd`
- Topic Tags: `binlog`, `pump`, `http-api`, `pd-urls`, `storage`, `security`, `tls`, `logging`, `retention`, `goleveldb`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0199_3640269ee0`
- Source ID: `tidb-docs-8.1:tidb-binlog/tidb-binlog-configuration-file.md#tidb-binlog-configuration-file`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c6d5eae953c9749713cbd3230ae483416309dbb37956345cf628154fe0d89b5c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-binlog/tidb-binlog-configuration-file#tidb-binlog-configuration-file
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-binlog/tidb-binlog-configuration-file.md

## Retrieval Guidance

- Use When: Use this chunk when looking up Pump configuration items for HTTP API addresses, PD connection settings, local binlog storage, retention, logging, TLS, or GoLevelDB-related storage options in TiDB Binlog.
- Retrieval Keywords: Pump, addr, advertise-addr, socket, pd-urls, data-dir, heartbeat-interval, gen-binlog-interval, gc, log-file, log-level, node-id, security, ssl-ca, ssl-cert, ssl-key, storage, sync-log, kv_chan_cap, slow_write_threshold, stop-write-at-available-space, kv, GoLevelDB, take a long time to write binlog, HTTP API, PD URLs
- Follow-up Guidance: For the detailed description of the `storage.kv` items such as `block-cache-capacity` and `write-buffer`, the source points to the GoLevelDB document.
- Classification Note: The official content is configuration documentation because it defines Pump configuration parameters, their meanings, and default values.

## Official Source Content

# TiDB Binlog Configuration File

This document introduces the configuration items of TiDB Binlog.
## Pump

This section introduces the configuration items of Pump. For the example of a complete Pump configuration file, see [Pump Configuration](https://github.com/pingcap/tidb-binlog/blob/release-8.1/cmd/pump/pump.toml).
### addr

* Specifies the listening address of HTTP API in the format of `host:port`.
* Default value: `127.0.0.1:8250`
### advertise-addr

* Specifies the externally accessible HTTP API address. This address is registered in PD in the format of `host:port`.
* Default value: `127.0.0.1:8250`
### socket

* The Unix socket address that HTTP API listens to.
* Default value: ""
### pd-urls

* Specifies the comma-separated list of PD URLs. If multiple addresses are specified, when the PD client fails to connect to one address, it automatically tries to connect to another address.
* Default value: `http://127.0.0.1:2379`
### data-dir

* Specifies the directory where binlogs and their indexes are stored locally.
* Default value: `data.pump`
### heartbeat-interval

* Specifies the heartbeat interval (in seconds) at which the latest status is reported to PD.
* Default value: `2`
### gen-binlog-interval

* Specifies the interval (in seconds) at which data is written into fake binlog.
* Default value: `3`
### gc

* Specifies the number of days (integer) that binlogs can be stored locally. Binlogs stored longer than the specified number of days are automatically deleted.
* Default value: `7`
### log-file

* Specifies the path where log files are stored. If the parameter is set to an empty value, log files are not stored.
* Default value: ""
### log-level

* Specifies the log level.
* Default value: `info`
### node-id

* Specifies the Pump node ID. With this ID, this Pump process can be identified in the cluster.
* Default value: `hostname:port number`. For example, `node-1:8250`.
### security

This section introduces configuration items related to security.
#### ssl-ca

* Specifies the file path of the trusted SSL certificate list or CA list. For example, `/path/to/ca.pem`.
* Default value: ""
#### ssl-cert

* Specifies the path of the X509 certificate file encoded in the Privacy Enhanced Mail (PEM) format. For example, `/path/to/pump.pem`.
* Default value: ""
#### ssl-key

* Specifies the path of the X509 key file encoded in the PEM format. For example, `/path/to/pump-key.pem`.
* Default value: ""
### storage

This section introduces configuration items related to storage.
#### sync-log

* Specifies whether to use `fsync` after each **batch** write to binlog to ensure data safety.
* Default value: `true`
#### kv_chan_cap

* Specifies the number of write requests that the buffer can store before Pump receives these requests.
* Default value: `1048576` (that is, 2 to the power of 20)
#### slow_write_threshold

* The threshold (in seconds). If it takes longer to write a single binlog file than this specified threshold, the write is considered slow write and `"take a long time to write binlog"` is output in the log.
* Default value: `1`
#### stop-write-at-available-space

* Binlog write requests is no longer accepted when the available storage space is below this specified value. You can use the format such as `900 MB`, `5 GB`, and `12 GiB` to specify the storage space. If there is more than one Pump node in the cluster, when a Pump node refuses a write request because of the insufficient space, TiDB will automatically write binlogs to other Pump nodes.
* Default value: `10 GiB`
#### kv

Currently the storage of Pump is implemented based on [GoLevelDB](https://github.com/syndtr/goleveldb). Under `storage` there is also a `kv` subgroup that is used to adjust the GoLevel configuration. The supported configuration items are shown as below:

* block-cache-capacity
* block-restart-interval
* block-size
* compaction-L0-trigger
* compaction-table-size
* compaction-total-size
* compaction-total-size-multiplier
* write-buffer
* write-L0-pause-trigger
* write-L0-slowdown-trigger

For the detailed description of the above items, see [GoLevelDB Document](https://godoc.org/github.com/syndtr/goleveldb/leveldb/opt#Options).
