# DM-master command-line flags

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-command-line-flags.md`
- Source Title: `TiDB Data Migration Command-line Flags`
- Source Heading Path: `TiDB Data Migration Command-line Flags | TiDB Data Migration Command-line Flags > DM-master | TiDB Data Migration Command-line Flags > DM-master > `--advertise-addr` | TiDB Data Migration Command-line Flags > DM-master > `--advertise-peer-urls` | TiDB Data Migration Command-line Flags > DM-master > `--config` | TiDB Data Migration Command-line Flags > DM-master > `--data-dir` | TiDB Data Migration Command-line Flags > DM-master > `--initial-cluster` | TiDB Data Migration Command-line Flags > DM-master > `--join` | TiDB Data Migration Command-line Flags > DM-master > `--log-file` | TiDB Data Migration Command-line Flags > DM-master > `-L` | TiDB Data Migration Command-line Flags > DM-master > `--master-addr` | TiDB Data Migration Command-line Flags > DM-master > `--name` | TiDB Data Migration Command-line Flags > DM-master > `--peer-urls` | TiDB Data Migration Command-line Flags > DM-master > `--secret-key-path``
- Source Line Ranges: `5-83`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: none
- Topic Tags: `command-line-flags`, `dm-master`, `addresses`, `cluster-bootstrap`, `join`, `logging`, `configuration`, `encryption`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0212_fe5e7bea7e`
- Source ID: `tidb-docs-8.1:dm/dm-command-line-flags.md#tidb-data-migration-command-line-flags`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `071883e122e54cd3d95c3f4e248025ecb8c4dc4223e8dc701bc0bc015015405b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-command-line-flags#tidb-data-migration-command-line-flags
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-command-line-flags.md

## Retrieval Guidance

- Use When: Use this chunk when you need the DM-master command-line flag meanings, defaults, required flags, or bootstrap and join address formats.
- Retrieval Keywords: DM-master command-line flags, --advertise-addr, --advertise-peer-urls, --config, --data-dir, --initial-cluster, --join, --log-file, -L, --master-addr, --name, --peer-urls, --secret-key-path, bootstrap DM-master cluster, DM-master joins this cluster, external address used to receive client requests, http(s)://domain-name:port
- Follow-up Guidance: The content includes example values for `--initial-cluster` in a 3-node cluster and for `--join` when a new DM-master node joins a 2-node cluster.
- Classification Note: This is reference content because it defines DM-master flags with their purpose, default value, and whether each flag is required or optional.

## Official Source Content

# TiDB Data Migration Command-line Flags

This document introduces DM's command-line flags.
## DM-master
### `--advertise-addr`

- The external address of DM-master used to receive client requests
- The default value is `"{master-addr}"`
- Optional flag. It can be in the form of `"domain-name:port"`
### `--advertise-peer-urls`

- The external address for communication between DM-master nodes
- The default value is `"{peer-urls}"`
- Optional flag. It can be in the form of `"http(s)://domain-name:port"`
### `--config`

- The configuration file path of DM-master
- The default value is `""`
- Optional flag
### `--data-dir`

- The directory used to store data of DM-master
- The default value is `"default.{name}"`
- Optional flag
### `--initial-cluster`

- The `"{node name}={external address}"` list used to bootstrap DM-master cluster
- The default value is `"{name}={advertise-peer-urls}"`
- This flag needs to be specified if the `join` flag is not specified. A configuration example of a 3-node cluster is `"dm-master-1=http://172.16.15.11:8291,dm-master-2=http://172.16.15.12:8291,dm-master-3=http://172.16.15.13:8291"`
### `--join`

- The existing cluster's `advertise-addr` list when a DM-master node joins this cluster
- The default value is `""`
- This flag needs to be specified if the `initial-cluster` flag is not specified. Suppose a new node joins a cluster that has 2 nodes, a configuration example is `"172.16.15.11:8261,172.16.15.12:8261"`
### `--log-file`

- The output file name of the log
- The default value is `""`
- Optional flag
### `-L`

- The log level
- The default value is `"info"`
- Optional flag
### `--master-addr`

- The address on which DM-master listens to the client's requests
- The default value is `""`
- Required flag
### `--name`

- The name of a DM-master node
- The default value is `"dm-master-{hostname}"`
- Required flag
### `--peer-urls`

- The listening address for communications between DM-master nodes
- The default value is `"http://127.0.0.1:8291"`
- Required flag
### `--secret-key-path`

- The path of the customized secret key for encryption and decryption
- The default value is `""`
- Optional flag
