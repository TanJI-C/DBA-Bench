# binlogctl overview, download, commands, and node state operations

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-binlog/binlog-control.md`
- Source Title: `binlogctl`
- Source Heading Path: `binlogctl | binlogctl > Download `binlogctl` | binlogctl > Descriptions`
- Source Line Ranges: `5-110`
- Source Scope: `self_managed`
- Primary Component: `ecosystem`
- Related Components: `pd`, `tidb`
- Topic Tags: `binlogctl`, `pump`, `drainer`, `node-state`, `pause`, `offline`, `update-state`, `pd-urls`, `ssl`, `toolkit`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0267_d1b217cae0`
- Source ID: `tidb-docs-8.1:tidb-binlog/binlog-control.md#binlogctl`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9f0e49312ee3ccd8d4d60bd6c7538e7b3388bcdfabd0245f6c2931aaec6a81c6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-binlog/binlog-control#binlogctl
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-binlog/binlog-control.md

## Retrieval Guidance

- Use When: Use this chunk when you need the binlogctl tool overview, supported commands, parameters, or examples for checking, pausing, offlining, or updating Pump and Drainer node state in a TiDB Binlog cluster.
- Retrieval Keywords: binlogctl, Binlog Control, TiDB Binlog, Pump, Drainer, pumps, drainers, update-pump, update-drainer, pause-pump, pause-drainer, offline-pump, offline-drainer, generate_meta, encrypt, -pd-urls, -node-id, -state, -show-offline-nodes, -ssl-ca, -ssl-cert, -ssl-key, check the state of Pump or Drainer, pause or close Pump or Drainer, modify the state of a Pump or Drainer node in abnormal states, bin/binlogctl -pd-urls=http://127.0.0.1:2379 -cmd pumps, bin/binlogctl -pd-urls=http://127.0.0.1:2379 -cmd drainers
- Follow-up Guidance: The source notes that update-pump or update-drainer directly modifies the Pump or Drainer state saved in PD and should not be used when the node runs normally because normal nodes regularly update their state to PD.
- Classification Note: This chunk is classified as an operation topic because it describes the binlogctl command line tool, its parameters, and operational procedures for querying and changing Pump and Drainer node states.

## Official Source Content

# binlogctl

[Binlog Control](https://github.com/pingcap/tidb-binlog/tree/release-8.1/binlogctl) (`binlogctl` for short) is a command line tool for TiDB Binlog. You can use `binlogctl` to manage TiDB Binlog clusters.

You can use `binlogctl` to:

* Check the state of Pump or Drainer
* Pause or close Pump or Drainer
* Handle the abnormal state of Pump or Drainer

The following are its usage scenarios:

* An error occurs during data replication or you need to check the running state of Pump or Drainer.
* You need to pause or close Pump or Drainer when maintaining the cluster.
* A Pump or Drainer process exits abnormally, while the node state is not updated or is unexpected. This affects the data replication task.
## Download `binlogctl`

`binlogctl` is included in the TiDB Toolkit. To download the TiDB Toolkit, see [Download TiDB Tools](https://docs.pingcap.com/tidb/stable/download-ecosystem-tools).
## Descriptions

Command line parameters:

```
Usage of binlogctl:
  -V    prints version and exit
  -cmd string
        operator: "generate_meta", "pumps", "drainers", "update-pump", "update-drainer", "pause-pump", "pause-drainer", "offline-pump", "offline-drainer", "encrypt" (default "pumps")
  -data-dir string
        meta directory path (default "binlog_position")
  -node-id string
        id of node, used to update some nodes with operations update-pump, update-drainer, pause-pump, pause-drainer, offline-pump and offline-drainer
  -pd-urls string
        a comma separated list of PD endpoints (default "http://127.0.0.1:2379")
  -show-offline-nodes
        include offline nodes when querying pumps/drainers
  -ssl-ca string
        Path of file that contains list of trusted SSL CAs for connection with cluster components.
  -ssl-cert string
        Path of file that contains X509 certificate in PEM format for connection with cluster components.
  -ssl-key string
        Path of file that contains X509 key in PEM format for connection with cluster components.
  -state string
        set node's state, can be set to online, pausing, paused, closing or offline.
  -text string
        text to be encrypted when using encrypt command
  -time-zone Asia/Shanghai
        set time zone if you want to save time info in savepoint file; for example, Asia/Shanghai for CST time, `Local` for local time
```

Command examples:

- Check the state of all the Pump or Drainer nodes.

    Set `cmd` to `pumps` or `drainers`. For example:

    ```bash
    bin/binlogctl -pd-urls=http://127.0.0.1:2379 -cmd pumps
    ```

    ```
    [2019/04/28 09:29:59.016 +00:00] [INFO] [nodes.go:48] ["query node"] [type=pump] [node="{NodeID: 1.1.1.1:8250, Addr: pump:8250, State: online, MaxCommitTS: 408012403141509121, UpdateTime: 2019-04-28 09:29:57 +0000 UTC}"]
    ```

    ```bash
    bin/binlogctl -pd-urls=http://127.0.0.1:2379 -cmd drainers
    ```

    ```
    [2019/04/28 09:29:59.016 +00:00] [INFO] [nodes.go:48] ["query node"] [type=drainer] [node="{NodeID: 1.1.1.1:8249, Addr: 1.1.1.1:8249, State: online, MaxCommitTS: 408012403141509121, UpdateTime: 2019-04-28 09:29:57 +0000 UTC}"]
    ```

- Pause or close Pump or Drainer.

    You can use the following commands to pause or close services:

    | Command             | Description           | Example                                                                                             |
    | :--------------- | :------------- | :------------------------------------------------------------------------------------------------|
    | pause-pump      | Pause Pump      | `bin/binlogctl -pd-urls=http://127.0.0.1:2379 -cmd pause-pump -node-id ip-127-0-0-1:8250`       |
    | pause-drainer   | Pause Drainer   | `bin/binlogctl -pd-urls=http://127.0.0.1:2379 -cmd pause-drainer -node-id ip-127-0-0-1:8249`    |
    | offline-pump    | Close Pump      | `bin/binlogctl -pd-urls=http://127.0.0.1:2379 -cmd offline-pump -node-id ip-127-0-0-1:8250`     |
    | offline-drainer | Close Drainer   | `bin/binlogctl -pd-urls=http://127.0.0.1:2379 -cmd offline-drainer -node-id ip-127-0-0-1:8249`  |

    `binlogctl` sends the HTTP request to the Pump or Drainer node. After receiving the request, the node executes the exiting procedures accordingly.

- Modify the state of a Pump or Drainer node in abnormal states.

    When a Pump or Drainer node runs normally or when it is paused or closed in the normal process, it is in the normal state. In abnormal states, the Pump or Drainer node cannot correctly maintain its state. This affects data replication tasks. In this case, use `binlogctl` to repair the state information.

    To update the state of a Pump or Drainer node, set `cmd` to `update-pump` or `update-drainer`. The state can be `paused` or `offline`. For example:

    ```bash
    bin/binlogctl -pd-urls=http://127.0.0.1:2379 -cmd update-pump -node-id ip-127-0-0-1:8250 -state paused
    ```

    > **Note:**
    >
    > When a Pump or Drainer node runs normally, it regularly updates its state to PD. The above command directly modifies the Pump or Drainer state saved in PD; therefore, do not use the command when the Pump or Drainer node runs normally. For more information, refer to [TiDB Binlog FAQ](https://docs.pingcap.com/tidb/stable/tidb-binlog/tidb-binlog-faq).
