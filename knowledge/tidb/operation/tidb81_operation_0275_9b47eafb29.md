# Pump and Drainer states, process lifecycle, and binlogctl operations

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-binlog/maintain-tidb-binlog-cluster.md`
- Source Title: `TiDB Binlog Cluster Operations`
- Source Heading Path: `TiDB Binlog Cluster Operations | TiDB Binlog Cluster Operations > Pump or Drainer state | TiDB Binlog Cluster Operations > Starting and exiting a Pump or Drainer process | TiDB Binlog Cluster Operations > Starting and exiting a Pump or Drainer process > Pump | TiDB Binlog Cluster Operations > Starting and exiting a Pump or Drainer process > Drainer | TiDB Binlog Cluster Operations > Use `binlogctl` to manage Pump/Drainer`
- Source Line Ranges: `5-55`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `pd`
- Topic Tags: `binlog`, `pump`, `drainer`, `node-state`, `startup`, `shutdown`, `pause`, `offline`, `binlogctl`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0275_9b47eafb29`
- Source ID: `tidb-docs-8.1:tidb-binlog/maintain-tidb-binlog-cluster.md#tidb-binlog-cluster-operations`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6d6b2d5227cdffe1d911aa5a95172c4171bf7d74e07001c7882fa395c1d93358`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-binlog/maintain-tidb-binlog-cluster#tidb-binlog-cluster-operations
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-binlog/maintain-tidb-binlog-cluster.md

## Retrieval Guidance

- Use When: Use this chunk when you need the defined Pump or Drainer states, process start and exit behavior, or the binlogctl operations for pausing, closing, or checking Pump and Drainer nodes in a TiDB Binlog cluster.
- Retrieval Keywords: online, pausing, paused, closing, offline, Pump or Drainer state, Starting and exiting a Pump or Drainer process, pause-pump, pause-drainer, offline-pump, offline-drainer, binlogctl, checking the state of Pump or Drainer, Pausing or closing Pump or Drainer, Handling the abnormal state of Pump or Drainer, PD, kill -9, Ctrl+C
- Follow-up Guidance: For detailed usage of binlogctl and how to pause, close, check, and modify the state of Drainer, the content points to the binlogctl guide and binlogctl overview.
- Classification Note: This is classified as an operation chunk because the content defines node lifecycle states and describes operational process control and binlogctl management for Pump and Drainer.

## Official Source Content

# TiDB Binlog Cluster Operations

This document introduces the following TiDB Binlog cluster operations:

+ The state of a Pump and Drainer nodes
+ Starting or exiting a Pump or Drainer process
+ Managing the TiDB Binlog cluster by using the binlogctl tool or by directly performing SQL operations in TiDB
## Pump or Drainer state

Pump or Drainer state description:

* `online`: running normally
* `pausing`: in the pausing process
* `paused`: has been stopped
* `closing`: in the offline process
* `offline`: has been offline

> **Note:**
>
> The state information of a Pump or Drainer node is maintained by the service itself and is regularly updated to the Placement Driver (PD).
## Starting and exiting a Pump or Drainer process
### Pump

* Starting: When started, the Pump node notifies all Drainer nodes in the `online` state. If the notification is successful, the Pump node sets its state to `online`. Otherwise, the Pump node reports an error, sets its state to `paused` and exits the process.
* Exiting: The Pump node enters the `paused` or `offline` state before the process is exited normally; if the process is exited abnormally (caused by the `kill -9` command, process panic, crash), the node is still in the `online` state.
    * Pause: You can pause a Pump process by using the `kill` command (not `kill -9`), pressing <kbd>Ctrl</kbd>+<kbd>C</kbd> or using the `pause-pump` command in the binlogctl tool. After receiving the pause instruction, the Pump node sets its state to `pausing`, stops receiving binlog write requests and stops providing binlog data to Drainer nodes. After all threads are safely exited, the Pump node updates its state to `paused` and exits the process.
    * Offline: You can close a Pump process only by using the `offline-pump` command in the binlogctl tool. After receiving the offline instruction, the Pump node sets its state to `closing` and stops receiving the binlog write requests. The Pump node continues providing binlog to Drainer nodes until all binlog data is consumed by Drainer nodes. Then, the Pump node sets its state to `offline` and exits the process.
### Drainer

* Starting: When started, the Drainer node sets its state to `online` and tries to pull binlogs from all Pump nodes which are not in the `offline` state. If it fails to get the binlogs, it keeps trying.
* Exiting: The Drainer node enters the `paused` or `offline` state before the process is exited normally; if the process is exited abnormally (caused by `kill -9`, process panic, crash), the Drainer node is still in the `online` state.
    * Pause: You can pause a Drainer process by using the `kill` command (not `kill -9`), pressing <kbd>Ctrl</kbd>+<kbd>C</kbd> or using the `pause-drainer` command in the binlogctl tool. After receiving the pause instruction, the Drainer node sets its state to `pausing` and stops pulling binlogs from Pump nodes. After all threads are safely exited, the Drainer node sets its state to `paused` and exits the process.
    * Offline: You can close a Drainer process only by using the `offline-drainer` command in the binlogctl tool. After receiving the offline instruction, the Drainer node sets its state to `closing` and stops pulling binlogs from Pump nodes. After all threads are safely exited, the Drainer node updates its state to `offline` and exits the process.

For how to pause, close, check, and modify the state of Drainer, see the [binlogctl guide](https://docs.pingcap.com/tidb/stable/tidb-binlog/binlog-control).
## Use `binlogctl` to manage Pump/Drainer

[`binlogctl`](https://github.com/pingcap/tidb-binlog/tree/release-8.1/binlogctl) is an operations tool for TiDB Binlog with the following features:

* Checking the state of Pump or Drainer
* Pausing or closing Pump or Drainer
* Handling the abnormal state of Pump or Drainer

For detailed usage of `binlogctl`, refer to [binlogctl overview](https://docs.pingcap.com/tidb/stable/tidb-binlog/binlog-control).
