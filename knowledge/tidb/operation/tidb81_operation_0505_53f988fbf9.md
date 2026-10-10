# Scale-in command purpose, component offline handling, and syntax

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-component-cluster-scale-in.md`
- Source Title: `tiup cluster scale-in`
- Source Heading Path: `tiup cluster scale-in | tiup cluster scale-in > Particular handling of components' offline process | tiup cluster scale-in > Syntax`
- Source Line Ranges: `5-36`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `pd`, `tikv`, `tiflash`, `tidb`
- Topic Tags: `scale-in`, `node-removal`, `offline-process`, `tombstone`, `prune`, `syntax`, `cluster-management`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0505_53f988fbf9`
- Source ID: `tidb-docs-8.1:tiup/tiup-component-cluster-scale-in.md#tiup-cluster-scale-in`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `30fa5944ee750747fde6982c6bdc88c99e3f85a335e1da64ce4d6cb3a2a786c0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-scale-in#tiup-cluster-scale-in
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-component-cluster-scale-in.md

## Retrieval Guidance

- Use When: Use this chunk when looking for what `tiup cluster scale-in` does, its command syntax, or how offline handling differs for TiKV, TiFlash, TiDB Binlog, PD, and other components during node removal.
- Retrieval Keywords: tiup cluster scale-in, scale in cluster, tiup cluster scale-in <cluster-name>, TiKV offline asynchronously, TiFlash offline asynchronously, TiDB Binlog offline asynchronously, Tombstone, tiup cluster display, tiup cluster prune, PD components offline through API, remove specified nodes from the cluster, deletes the remaining files
- Follow-up Guidance: For TiKV, TiFlash, and TiDB Binlog nodes being scaled in, the content says to check `tiup cluster display` until the status becomes `Tombstone` and then execute `tiup cluster prune` to clean up the nodes.
- Classification Note: This is classified as an operation chunk because the official content describes the purpose, component-specific offline process, and command syntax for scaling in a cluster.

## Official Source Content

# tiup cluster scale-in

The `tiup cluster scale-in` command is used to scale in the cluster, which takes the services of the specified nodes offline, removes the specified nodes from the cluster, and deletes the remaining files from those nodes.
## Particular handling of components' offline process

Because the TiKV, TiFlash, and TiDB Binlog components are taken offline asynchronously (which requires TiUP to remove the node through API first) and the stopping process takes a long time (which requires TiUP to continuously check whether the node is successfully taken offline), the TiKV, TiFlash, and TiDB Binlog components are handled particularly as follows:

- For TiKV, TiFlash, and TiDB Binlog components:

    1. TiUP Cluster takes the node offline through API and directly exits without waiting for the process to be completed.
    2. To check the status of the nodes being scaled in, you need to execute the `tiup cluster display` command and wait for the status to become `Tombstone`.
    3. To clean up the nodes in the `Tombstone` status, you need to execute the `tiup cluster prune` command. The `tiup cluster prune` command performs the following operations:

        - Stops the services of the nodes that have been taken offline.
        - Cleans up the data files of the nodes that have been taken offline.
        - Updates the cluster topology and removes the nodes that have been taken offline.

For other components:

- When taking the PD components offline, TiUP Cluster quickly deletes the specified nodes from the cluster through API, stops the service of the specified PD nodes, and then deletes the related data files from the nodes.
- When taking other components down, TiUP Cluster directly stops the node services and deletes the related data files from the specified nodes.
## Syntax

```shell
tiup cluster scale-in <cluster-name> [flags]
```

`<cluster-name>` is the name of the cluster to scale in. If you forget the cluster name, you can check it using the [`tiup cluster list`](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-list) command.
