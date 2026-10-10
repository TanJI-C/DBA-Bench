# Pause and offline handling for Pump and Drainer nodes

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-binlog/tidb-binlog-faq.md`
- Source Title: `TiDB Binlog FAQs`
- Source Heading Path: `TiDB Binlog FAQs > How can I close a Pump or Drainer node? | TiDB Binlog FAQs > When can I use the `update-pump` command in binlogctl to set the Pump state to `offline`? | TiDB Binlog FAQs > Can I use the `update-pump` command in binlogctl to set the Pump state to `offline` if I want to close a Pump node that is exited and set to `paused`? | TiDB Binlog FAQs > When can I use the `update-drainer` command in binlogctl to set the Drainer state to `offline`? | TiDB Binlog FAQs > Can I use SQL operations such as `change pump` and `change drainer` to pause or close the Pump or Drainer service?`
- Source Line Ranges: `207-237`
- Source Scope: `shared`
- Primary Component: `tidb`
- Related Components: `pd`
- Topic Tags: `pump`, `drainer`, `binlogctl`, `offline`, `paused`, `sql-operations`, `node-state`, `data-loss-warning`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0278_744dfcbb7a`
- Source ID: `tidb-docs-8.1:tidb-binlog/tidb-binlog-faq.md#how-can-i-close-a-pump-or-drainer-node`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `472ecabc6a4d6d99f536bf09b2cd1709188fea6842a1dc6a6216c428bc45e338`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-binlog/tidb-binlog-faq#how-can-i-close-a-pump-or-drainer-node
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-binlog/tidb-binlog-faq.md

## Retrieval Guidance

- Use When: Use this chunk when asking how to pause, close, or mark Pump or Drainer nodes as offline with binlogctl, including paused nodes and SQL state changes in PD.
- Retrieval Keywords: offline-pump, offline-drainer, update-pump, update-drainer, binlogctl, change pump, change drainer, paused, offline, PD, binlog data loss, data inconsistency between upstream and downstream, stale Pump nodes, stale Drainer nodes
- Follow-up Guidance: The source distinguishes regular closure with `offline-pump` or `offline-drainer` from state changes with `update-pump` or `update-drainer`, and notes that SQL operations such as `change pump` and `change drainer` directly modify state information saved in PD.
- Classification Note: This is classified as operation because the content explains operational handling of Pump and Drainer node states, including when to use `offline-pump`, `offline-drainer`, `update-pump`, and `update-drainer`.

## Official Source Content

## How can I close a Pump or Drainer node?

Currently, you can only use the `offline-pump` or `offline-drainer` command in binlogctl to close a Pump or Drainer node.
## When can I use the `update-pump` command in binlogctl to set the Pump state to `offline`?

You can use the `update-pump` command to set the Pump state to `offline` in the following situations:

- When a Pump process is exited abnormally and the service cannot be recovered, the replication task is interrupted. If you want to recover the replication and accept some losses of binlog data, use the `update-pump` command to set the Pump state to `offline`. Then, the Drainer node stops pulling binlog from the Pump node and continues replicating data.
- Some stale Pump nodes are left over from historical tasks. Their processes have been exited and their services are no longer needed. Then, use the `update-pump` command to set their state to `offline`.

For other situations, use the `offline-pump` command to close the Pump service, which is the regular process.

> **Warning:**
>
> > Do not use the `update-pump` command unless you can tolerate binlog data loss and data inconsistency between upstream and downstream, or you no longer need the binlog data stored in the Pump node.
## Can I use the `update-pump` command in binlogctl to set the Pump state to `offline` if I want to close a Pump node that is exited and set to `paused`?

When a Pump process is exited and the node is in the `paused` state, not all the binlog data in the node is consumed in its downstream Drainer node. Therefore, doing so might risk data inconsistency between upstream and downstream. In this situation, restart the Pump and use the `offline-pump` command to close the Pump node.
## When can I use the `update-drainer` command in binlogctl to set the Drainer state to `offline`?

Some stale Drainer nodes are left over from historical tasks. Their processes have been exited and their services are no longer needed. Then, use the `update-drainer` command to set their state to `offline`.
## Can I use SQL operations such as `change pump` and `change drainer` to pause or close the Pump or Drainer service?

No. For more details on these SQL operations, refer to [Use SQL statements to manage Pump or Drainer](https://docs.pingcap.com/tidb/stable/tidb-binlog/maintain-tidb-binlog-cluster#use-sql-statements-to-manage-pump-or-drainer).

These SQL operations directly modifies the state information saved in PD and are functionally equivalent to the `update-pump` and `update-drainer` commands in binlogctl. To pause or close the Pump or Drainer service, use the binlogctl tool.
