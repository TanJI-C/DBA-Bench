# DM-worker and dmctl command-line flags

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-command-line-flags.md`
- Source Title: `TiDB Data Migration Command-line Flags`
- Source Heading Path: `TiDB Data Migration Command-line Flags > DM-worker | TiDB Data Migration Command-line Flags > DM-worker > `--advertise-addr` | TiDB Data Migration Command-line Flags > DM-worker > `--config` | TiDB Data Migration Command-line Flags > DM-worker > `--join` | TiDB Data Migration Command-line Flags > DM-worker > `--log-file` | TiDB Data Migration Command-line Flags > DM-worker > `-L` | TiDB Data Migration Command-line Flags > DM-worker > `--name` | TiDB Data Migration Command-line Flags > DM-worker > `--worker-addr` | TiDB Data Migration Command-line Flags > dmctl | TiDB Data Migration Command-line Flags > dmctl > `--config` | TiDB Data Migration Command-line Flags > dmctl > `--master-addr``
- Source Line Ranges: `84-140`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: none
- Topic Tags: `command-line-flags`, `dm-worker`, `dmctl`, `addresses`, `registration`, `logging`, `configuration`, `cluster-connection`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0213_2d6b048b26`
- Source ID: `tidb-docs-8.1:dm/dm-command-line-flags.md#dm-worker`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `85873a072c44d959abfd5dfbddd771213a146841691e0255564d1c09765292f6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-command-line-flags#dm-worker
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-command-line-flags.md

## Retrieval Guidance

- Use When: Use this chunk when you need the DM-worker or dmctl command-line flag definitions, especially registration to a DM-master cluster or connecting dmctl to a DM-master node.
- Retrieval Keywords: DM-worker command-line flags, dmctl command-line flags, --advertise-addr, --config, --join, --log-file, -L, --name, --worker-addr, --master-addr, DM-worker registers to this cluster, advertise-addr list of DM-master nodes, dmctl interacts with DM-master, configuration file path of dmctl, configuration file path of DM-worker
- Follow-up Guidance: The content provides a 3-node DM-master cluster example for the DM-worker `--join` flag and states that dmctl `--master-addr` is required when dmctl interacts with DM-master.
- Classification Note: This is reference content because it lists DM-worker and dmctl flags with their meanings, default values, and required usage conditions.

## Official Source Content

## DM-worker
### `--advertise-addr`

- The external address of DM-worker used to receive client requests
- The default value is `"{worker-addr}"`
- Optional flag. It can be in the form of `"domain-name:port"`
### `--config`

- The configuration file path of DM-worker
- The default value is `""`
- Optional flag
### `--join`

- The `{advertise-addr}` list of DM-master nodes in a cluster when a DM-worker registers to this cluster
- The default value is `""`
- Required flag. A configuration example of 3-node (DM-master node) cluster is `"172.16.15.11:8261,172.16.15.12:8261,172.16.15.13:8261"`
### `--log-file`

- The output file name of the log
- The default value is `""`
- Optional flag
### `-L`

- The log level
- The default value is `"info"`
- Optional flag
### `--name`

- The name of a DM-worker node
- The default value is `"{advertise-addr}"`
- Required flag
### `--worker-addr`

- The address on which DM-worker listens to the client's requests
- The default value is `""`
- Required flag
## dmctl
### `--config`

- The configuration file path of dmctl
- The default value is `""`
- Optional flag
### `--master-addr`

- The `{advertise-addr}` of any DM-master node in the cluster to be connected by dmctl
- The default value is `""`
- It is a required flag when dmctl interacts with DM-master
