# TiDB Binlog FAQ: pausing, closing, and state changes for Pump and Drainer

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-binlog/tidb-binlog-faq.md`
- Source Title: `TiDB Binlog FAQs`
- Source Heading Path: `TiDB Binlog FAQs > When can I pause or close a Pump or Drainer node? | TiDB Binlog FAQs > How can I pause a Pump or Drainer process? | TiDB Binlog FAQs > Can I use the `update-pump` or `update-drainer` command in binlogctl to pause the Pump or Drainer service? | TiDB Binlog FAQs > Can I use the `update-pump` or `update-drainer` command in binlogctl to close the Pump or Drainer service? | TiDB Binlog FAQs > When can I use the `update-pump` command in binlogctl to set the Pump state to `paused`? | TiDB Binlog FAQs > When can I use the `update-drainer` command in binlogctl to set the Drainer state to `paused`?`
- Source Line Ranges: `145-206`
- Source Scope: `shared`
- Primary Component: `tidb`
- Related Components: `pd`, `shared`
- Topic Tags: `pump`, `drainer`, `binlogctl`, `pause`, `offline`, `state-management`, `process-control`, `upgrade`, `maintenance`, `data-consistency`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0277_e769f5ea95`
- Source ID: `tidb-docs-8.1:tidb-binlog/tidb-binlog-faq.md#when-can-i-pause-or-close-a-pump-or-drainer-node`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1e44b0f0c358a78b7f6a4c9dd42f77d055fcc863bf011e4f002b6031a9bbb8d8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-binlog/tidb-binlog-faq#when-can-i-pause-or-close-a-pump-or-drainer-node
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-binlog/tidb-binlog-faq.md

## Retrieval Guidance

- Use When: Use this chunk when operating Pump or Drainer state, including pausing processes, closing services, and understanding when `update-pump` or `update-drainer` can or cannot change state.
- Retrieval Keywords: When can I pause or close a Pump or Drainer node, TiDB Binlog Cluster Operations, Version upgrade, Server maintenance, Pump scale-in, Cancelling replication tasks, Service migration, How can I pause a Pump or Drainer process, Do not use the `kill -9` command, Ctrl+C, pause-pump, pause-drainer, update-pump, update-drainer, PD, offline, paused, online, data replication, data loss, data inconsistency, notify drainer ... error, restart the Pump node
- Follow-up Guidance: The content distinguishes normal pause methods such as killing the process without `kill -9`, `Ctrl+C`, or `pause-pump` and `pause-drainer`, from abnormal situations where `update-pump` or `update-drainer` is used only to correct stale state in PD.
- Classification Note: This chunk is classified as operation because it describes service state management, process control, and safe versus unsafe uses of binlogctl state change commands for Pump and Drainer.

## Official Source Content

## When can I pause or close a Pump or Drainer node?

Refer to [TiDB Binlog Cluster Operations](https://docs.pingcap.com/tidb/stable/tidb-binlog/maintain-tidb-binlog-cluster) to learn the description of the Pump or Drainer state and how to start and exit the process.

Pause a Pump or Drainer node when you need to temporarily stop the service. For example:

- Version upgrade

  Use the new binary to restart the service after the process is stopped.

- Server maintenance

  When the server needs a downtime maintenance, exit the process and restart the service after the maintenance is finished.

Close a Pump or Drainer node when you no longer need the service. For example:

- Pump scale-in

  If you do not need too many Pump services, close some of them.

- Cancelling replication tasks

  If you no longer need to replicate data to a downstream database, close the corresponding Drainer node.

- Service migration

  If you need to migrate the service to another server, close the service and re-deploy it on the new server.
## How can I pause a Pump or Drainer process?

- Directly kill the process.

    > **Note:**
    >
    > Do not use the `kill -9` command. Otherwise, the Pump or Drainer node cannot process signals.

- If the Pump or Drainer node runs in the foreground, pause it by pressing <kbd>Ctrl</kbd>+<kbd>C</kbd>.
- Use the `pause-pump` or `pause-drainer` command in binlogctl.
## Can I use the `update-pump` or `update-drainer` command in binlogctl to pause the Pump or Drainer service?

No. The `update-pump` or `update-drainer` command directly modifies the state information saved in PD without notifying Pump or Drainer to perform the corresponding operation. Misusing the two commands can interrupt data replication and might even cause data loss.
## Can I use the `update-pump` or `update-drainer` command in binlogctl to close the Pump or Drainer service?

No. The `update-pump` or `update-drainer` command directly modifies the state information saved in PD without notifying Pump or Drainer to perform the corresponding operation. Misusing the two commands interrupts data replication and might even cause data inconsistency. For example:

- When a Pump node runs normally or is in the `paused` state, if you use the `update-pump` command to set the Pump state to `offline`, the Drainer node stops pulling the binlog data from the `offline` Pump. In this situation, the newest binlog cannot be replicated to the Drainer node, causing data inconsistency between upstream and downstream.
- When a Drainer node runs normally, if you use the `update-drainer` command to set the Drainer state to `offline`, the newly started Pump node only notifies Drainer nodes in the `online` state. In this situation, the `offline` Drainer fails to pull the binlog data from the Pump node in time, causing data inconsistency between upstream and downstream.
## When can I use the `update-pump` command in binlogctl to set the Pump state to `paused`?

In some abnormal situations, Pump fails to correctly maintain its state. Then, use the `update-pump` command to modify the state.

For example, when a Pump process is exited abnormally (caused by directly exiting the process when a panic occurs or mistakenly using the `kill -9` command to kill the process), the Pump state information saved in PD is still `online`. In this situation, if you do not need to restart Pump to recover the service at the moment, use the `update-pump` command to update the Pump state to `paused`. Then, interruptions can be avoided when TiDB writes binlogs and Drainer pulls binlogs.
## When can I use the `update-drainer` command in binlogctl to set the Drainer state to `paused`?

In some abnormal situations, the Drainer node fails to correctly maintain its state, which has influenced the replication task. Then, use the `update-drainer` command to modify the state.

For example, when a Drainer process is exited abnormally (caused by directly exiting the process when a panic occurs or mistakenly using the `kill -9` command to kill the process), the Drainer state information saved in PD is still `online`. When a Pump node is started, it fails to notify the exited Drainer node (the `notify drainer ...` error), which cause the Pump node failure. In this situation, use the `update-drainer` command to update the Drainer state to `paused` and restart the Pump node.
