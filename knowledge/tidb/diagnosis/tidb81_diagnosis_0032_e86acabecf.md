# DM operational error handling for heartbeat, master restart, dmctl, relay, and charset issues

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-faq.md`
- Source Title: `TiDB Data Migration FAQs`
- Source Heading Path: `TiDB Data Migration FAQs > In DM v2.0, how do I handle the error "heartbeat config is different from previous used: serverID not equal" when switching the connection between DM-workers and MySQL instances in a virtual IP environment with the `heartbeat` feature enabled? | TiDB Data Migration FAQs > Why does a DM-master fail to join the cluster after it restarts and DM reports the error "fail to start embed etcd, RawCause: member xxx has already been bootstrapped"? | TiDB Data Migration FAQs > Why DM-master cannot be connected when I use dmctl to execute commands? | TiDB Data Migration FAQs > How to handle the returned error when executing start-relay command for DM versions from 2.0.2 to 2.0.6? | TiDB Data Migration FAQs > Why does the load unit report the `Unknown character set` error?`
- Source Line Ranges: `355-401`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tiup`, `sql`, `tidb`
- Topic Tags: `heartbeat`, `virtual-ip`, `dm-master`, `etcd`, `data-dir`, `dmctl`, `https-proxy`, `relay-log`, `upgrade`, `character-set`, `full-import`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0032_e86acabecf`
- Source ID: `tidb-docs-8.1:dm/dm-faq.md#in-dm-v2-0-how-do-i-handle-the-error-heartbeat-config-is-different-from-previous-used-serverid-not-equal-when-switching-the-connection-between-dm-workers-and-mysql-instances-in-a-virtual-ip-environment-with-the-heartbeat-feature-enabled`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `95d20bbf652430a58b035d26a1cf1bc10b645061193eee0b3712cce97c46abcb`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-faq#in-dm-v2-0-how-do-i-handle-the-error-heartbeat-config-is-different-from-previous-used-serverid-not-equal-when-switching-the-connection-between-dm-workers-and-mysql-instances-in-a-virtual-ip-environment-with-the-heartbeat-feature-enabled
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-faq.md

## Retrieval Guidance

- Use When: Use this chunk when troubleshooting DM operational errors involving `heartbeat` in virtual IP environments, DM-master restart and embedded etcd bootstrap state, dmctl connection failures related to proxy variables, `start-relay` local meta errors, or `Unknown character set` during full import.
- Retrieval Keywords: heartbeat config is different from previous used: serverID not equal, enable-heartbeat, virtual IP environment, DM-worker, DM-master, fail to start embed etcd, RawCause: member xxx has already been bootstrapped, data-dir, absolute paths, dmctl, --master-addr, RawCause: context deadline exceeded, https_proxy, http_proxy, no_proxy, https_proxy="" ./dmctl --master-addr "x.x.x.x:8261", start-relay, stop-relay, flush local meta, Rawcause: open relay-dir/xxx.000001/relay.metayyyy: no such file or directory, v2.0.2 to v2.0.6, v2.0.7, Unknown character set, load unit, full import, character sets supported by TiDB
- Follow-up Guidance: The content gives specific follow-up handling for each error, including disabling `enable-heartbeat`, using absolute `data-dir` paths, checking `https_proxy` and related proxy variables, restarting relay log or upgrading to v2.0.7 or later, and pre-creating downstream schema with character sets supported by TiDB.
- Classification Note: This chunk is classified as diagnosis because it groups several DM FAQ troubleshooting cases and explains the error conditions, causes, and corresponding handling steps for connectivity, relay, restart, heartbeat, and charset problems.

## Official Source Content

## In DM v2.0, how do I handle the error "heartbeat config is different from previous used: serverID not equal" when switching the connection between DM-workers and MySQL instances in a virtual IP environment with the `heartbeat` feature enabled?

The `heartbeat` feature is disabled by default in DM v2.0 and later versions. If you enable the feature in the task configuration file, it interferes with the high availability feature. To solve this issue, you can disable the `heartbeat` feature by setting `enable-heartbeat` to `false` in the task configuration file, and then reload the task configuration file. DM will forcibly disable the `heartbeat` feature in subsequent releases.
## Why does a DM-master fail to join the cluster after it restarts and DM reports the error "fail to start embed etcd, RawCause: member xxx has already been bootstrapped"?

When a DM-master starts, DM records the etcd information in the current directory. If the directory changes after the DM-master restarts, DM cannot get access to the etcd information, and thus the restart fails.

To solve this issue, you are recommended to maintain DM clusters using TiUP. In the case that you need to deploy using binary files, you need to configure `data-dir` with absolute paths in the configuration file of the DM-master, or pay attention to the current directory where you run the command.
## Why DM-master cannot be connected when I use dmctl to execute commands?

When using dmctl execute commands, you might find the connection to DM master fails (even if you have specified the parameter value of `--master-addr` in the command), and the error message is like `RawCause: context deadline exceeded, Workaround: please check your network connection.`. But after checking the network connection using commands like `telnet <master-addr>`, no exception is found.

In this case, you can check the environment variable `https_proxy` (note that it is **https**). If this variable is configured, dmctl automatically connects the host and port specified by `https_proxy`. If the host does not have a corresponding `proxy` forwarding service, the connection fails.

To solve this issue, check whether `https_proxy` is mandatory. If not, cancel the setting. Otherwise, add the environment variable setting `https_proxy="" ./dmctl --master-addr "x.x.x.x:8261"` before the oringial dmctl commands.

> **Note:**
>
> The environment variables related to `proxy` include `http_proxy`, `https_proxy`, and `no_proxy`. If the connection error persists after you perform the above steps, check whether the configuration parameters of `http_proxy` and `no_proxy` are correct.
## How to handle the returned error when executing start-relay command for DM versions from 2.0.2 to 2.0.6?

```
flush local meta, Rawcause: open relay-dir/xxx.000001/relay.metayyyy: no such file or directory
```

The above error might be made in the following cases:

- DM has been upgraded from v2.0.1 and earlier to v2.0.2 - v2.0.6, and relay log is started before the upgrade and restarted after the upgrade.
- Execute the stop-relay command to pause the relay log and then restart it.

You can avoid this error by the following options:

- Restart relay log:

    ```
    » stop-relay -s sourceID workerName
    » start-relay -s sourceID workerName
    ```

- Upgrade DM to v2.0.7 or later versions.
## Why does the load unit report the `Unknown character set` error?

TiDB does not support all MySQL character sets. Therefore, DM reports this error if an unsupported character set is used when creating the table schema during a full import. To bypass this error, you can create the table schema in the downstream in advance using the [character sets supported by TiDB](https://docs.pingcap.com/tidb/stable/character-set-and-collation) according to the specific data.
