# Connect to, inspect, and resize a TiUP Playground cluster

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-playground.md`
- Source Title: `Quickly Deploy a Local TiDB Cluster`
- Source Heading Path: `Quickly Deploy a Local TiDB Cluster > Quickly connect to the TiDB cluster started by playground | Quickly Deploy a Local TiDB Cluster > View information of the started cluster | Quickly Deploy a Local TiDB Cluster > Scale out a cluster | Quickly Deploy a Local TiDB Cluster > Scale in a cluster`
- Source Line Ranges: `92-136`
- Source Scope: `developer`
- Primary Component: `tiup`
- Related Components: `tidb`
- Topic Tags: `client`, `display`, `scale-out`, `scale-in`, `pid`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0524_86c7e1ede6`
- Source ID: `tidb-docs-8.1:tiup/tiup-playground.md#quickly-connect-to-the-tidb-cluster-started-by-playground`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e5292db6e04a7b0a0eba48463517c9470118cf0a0f886f8b2738c40902957593`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-playground#quickly-connect-to-the-tidb-cluster-started-by-playground
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-playground.md

## Retrieval Guidance

- Use When: Use this chunk when the user wants to connect to a local playground cluster, display running instance information, or scale playground components out or in by PID.
- Retrieval Keywords: tiup client, connect to a local TiDB cluster started by playground, built-in MySQL client, tiup playground display, Pid Role Uptime, tiup playground scale-out --db 2, tiup playground scale-in --pid 86526, view the pid
- Follow-up Guidance: The source says to execute `tiup playground display` to view the `pid` before using `tiup playground scale-in --pid` on a corresponding instance.
- Classification Note: This is classified as an operation chunk because it covers interactive connection, runtime inspection output, and resize commands for a TiUP Playground cluster.

## Official Source Content

## Quickly connect to the TiDB cluster started by playground

TiUP provides the `client` component, which is used to automatically find and connect to a local TiDB cluster started by playground. The usage is as follows:

```shell
tiup client
```

This command provides a list of TiDB clusters that are started by playground on the current machine on the console. Select the TiDB cluster to be connected. After clicking <kbd>Enter</kbd>, a built-in MySQL client is opened to connect to TiDB.
## View information of the started cluster

```shell
tiup playground display
```

The command above returns the following results:

```
Pid    Role     Uptime
---    ----     ------
84518  pd       35m22.929404512s
84519  tikv     35m22.927757153s
84520  pump     35m22.92618275s
86189  tidb     exited
86526  tidb     34m28.293148663s
86190  drainer  35m19.91349249s
```
## Scale out a cluster

The command-line parameter for scaling out a cluster is similar to that for starting a cluster. You can scale out two TiDB instances by executing the following command:

```shell
tiup playground scale-out --db 2
```
## Scale in a cluster

You can specify a `pid` in the `tiup playground scale-in` command to scale in the corresponding instance. To view the `pid`, execute `tiup playground display`.

```shell
tiup playground scale-in --pid 86526
```
