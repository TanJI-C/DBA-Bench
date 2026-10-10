# PD core bootstrap and cluster timing configuration

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/pd-configuration-file.md`
- Source Title: `PD Configuration File`
- Source Heading Path: `PD Configuration File | PD Configuration File > `name` | PD Configuration File > `data-dir` | PD Configuration File > `client-urls` | PD Configuration File > `advertise-client-urls` | PD Configuration File > `peer-urls` | PD Configuration File > `advertise-peer-urls` | PD Configuration File > `initial-cluster` | PD Configuration File > `initial-cluster-state` | PD Configuration File > `initial-cluster-token` | PD Configuration File > `lease` | PD Configuration File > `quota-backend-bytes` | PD Configuration File > `auto-compaction-mod` | PD Configuration File > `auto-compaction-retention` | PD Configuration File > `tick-interval` | PD Configuration File > `election-interval` | PD Configuration File > `enable-prevote` | PD Configuration File > `force-new-cluster` | PD Configuration File > `tso-update-physical-interval``
- Source Line Ranges: `5-127`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: none
- Topic Tags: `bootstrap`, `node-identity`, `storage-paths`, `client-endpoints`, `peer-endpoints`, `cluster-initialization`, `raft`, `election`, `lease`, `etcd`, `compaction`, `tso`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0124_5f149da9ad`
- Source ID: `tidb-docs-8.1:pd-configuration-file.md#pd-configuration-file`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `27c2642e04e295fb29c0f40eef439f5d5033b37cfb758f884eacc4ca8ebd64c0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/pd-configuration-file#pd-configuration-file
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/pd-configuration-file.md

## Retrieval Guidance

- Use When: Use this chunk when looking for PD bootstrap, endpoint, embedded etcd timing, lease, compaction, or TSO physical time configuration items in the PD configuration file.
- Retrieval Keywords: name, data-dir, client-urls, advertise-client-urls, peer-urls, advertise-peer-urls, initial-cluster, initial-cluster-state, initial-cluster-token, lease, quota-backend-bytes, auto-compaction-mod, auto-compaction-retention, tick-interval, election-interval, enable-prevote, force-new-cluster, tso-update-physical-interval, heartbeat-interval, election-timeout, Raft pre-vote, embedded etcd, PD Leader Key lease
- Follow-up Guidance: The source also points to command-line flags for PD configuration and to Modify the configuration for adjusting configuration values.
- Classification Note: This chunk is classified as PD configuration because it defines PD node identity, storage paths, client and peer URLs, cluster bootstrap settings, embedded etcd and Raft timing, and TSO update interval parameters.

## Official Source Content

# PD Configuration File

The PD configuration file supports more options than command-line parameters. You can find the default configuration file [here](https://github.com/pingcap/pd/blob/release-8.1/conf/config.toml).

This document only describes parameters that are not included in command-line parameters. Check [here](https://docs.pingcap.com/tidb/stable/command-line-flags-for-pd-configuration) for the command line parameters.

> **Tip:**
>
> If you need to adjust the value of a configuration item, refer to [Modify the configuration](https://docs.pingcap.com/tidb/stable/maintain-tidb-using-tiup#modify-the-configuration).
### `name`

- The unique name of a PD node
- Default value: `"pd"`
- To start multiply PD nodes, use a unique name for each node.
### `data-dir`

- The directory in which PD stores data
- Default value: `default.${name}"`
### `client-urls`

- The list of client URLs to be listened to by PD
- Default value: `"http://127.0.0.1:2379"`
- When you deploy a cluster, you must specify the IP address of the current host as `client-urls` (for example, `"http://192.168.100.113:2379"`). If the cluster runs on Docker, specify the IP address of Docker as `"http://0.0.0.0:2379"`.
### `advertise-client-urls`

- The list of advertise URLs for the client to access PD
- Default value: `"${client-urls}"`
- In some situations such as in the Docker or NAT network environment, if a client cannot access PD through the default client URLs listened to by PD, you must manually set the advertise client URLs.
- For example, the internal IP address of Docker is `172.17.0.1`, while the IP address of the host is `192.168.100.113` and the port mapping is set to `-p 2380:2380`. In this case, you can set `advertise-client-urls` to `"http://192.168.100.113:2380"`. The client can find this service through `"http://192.168.100.113:2380"`.
### `peer-urls`

- The list of peer URLs to be listened to by a PD node
- Default value: `"http://127.0.0.1:2380"`
- When you deploy a cluster, you must specify `peer-urls` as the IP address of the current host, such as `"http://192.168.100.113:2380"`. If the cluster runs on Docker, specify the IP address of Docker as `"http://0.0.0.0:2380"`.
### `advertise-peer-urls`

- The list of advertise URLs for other PD nodes (peers) to access a PD node
- Default: `"${peer-urls}"`
- In some situations such as in the Docker or NAT network environment, if the other nodes (peers) cannot access the PD node through the default peer URLs listened to by this PD node, you must manually set the advertise peer URLs.
- For example, the internal IP address of Docker is `172.17.0.1`, while the IP address of the host is `192.168.100.113` and the port mapping is set to `-p 2380:2380`. In this case, you can set `advertise-peer-urls` to `"http://192.168.100.113:2380"`. The other PD nodes can find this service through `"http://192.168.100.113:2380"`.
### `initial-cluster`

- The initial cluster configuration for bootstrapping
- Default value: `"{name}=http://{advertise-peer-url}"`
- For example, if `name` is "pd", and `advertise-peer-urls` is `"http://192.168.100.113:2380"`, the `initial-cluster` is `"pd=http://192.168.100.113:2380"`.
- If you need to start three PD servers, the `initial-cluster` might be:

    ```
    pd1=http://192.168.100.113:2380, pd2=http://192.168.100.114:2380, pd3=192.168.100.115:2380
    ```
### `initial-cluster-state`

+ The initial state of the cluster
+ Default value: `"new"`
### `initial-cluster-token`

+ Identifies different clusters during the bootstrap phase
+ Default value: `"pd-cluster"`
+ If multiple clusters that have nodes with same configurations are deployed successively, you must specify different tokens to isolate different cluster nodes.
### `lease`

+ The timeout of the PD Leader Key lease. After the timeout, the system re-elects a Leader.
+ Default value: `3`
+ Unit: second
### `quota-backend-bytes`

+ The storage size of the meta-information database, which is 8GiB by default
+ Default value: `8589934592`
### `auto-compaction-mod`

+ The automatic compaction modes of the meta-information database
+ Available options: `periodic` (by cycle) and `revision` (by version number).
+ Default value: `periodic`
### `auto-compaction-retention`

+ The time interval for automatic compaction of the meta-information database when `auto-compaction-retention` is `periodic`. When the compaction mode is set to `revision`, this parameter indicates the version number for the automatic compaction.
+ Default value: 1h
### `tick-interval`

+ Equivalent to the `heartbeat-interval` configuration item of etcd. It controls the Raft heartbeat interval between embedded etcd instances in different PD nodes. A smaller value accelerates failure detection but increases network load.
+ Default value: `500ms`
### `election-interval`

+ Equivalent to the `election-timeout` configuration item of etcd. It controls the election timeout for embedded etcd instances in PD nodes. If an etcd instance does not receive a valid heartbeat from other etcd instances within this period, it initiates a Raft election.
+ Default value: `3000ms`
+ This value must be at least five times the [`tick-interval`](#tick-interval). For example, if `tick-interval` is `500ms`, `election-interval` must be greater than or equal to `2500ms`.
### `enable-prevote`

+ Equivalent to the `pre-vote` configuration item of etcd. It controls whether the embedded etcd in the PD node enables Raft pre-vote. When enabled, etcd performs an additional election phase to check whether enough votes can be obtained to win the election, minimizing service disruption.
+ Default value: `true`
### `force-new-cluster`

+ Determines whether to force PD to start as a new cluster and modify the number of Raft members to `1`
+ Default value: `false`
### `tso-update-physical-interval`

+ The interval at which PD updates the physical time of TSO.
+ In a default update interval of TSO physical time, PD provides at most 262144 TSOs. To get more TSOs, you can reduce the value of this configuration item. The minimum value is `1ms`.
+ Decreasing this configuration item might increase the CPU usage of PD. According to the test, compared with the interval of `50ms`, the [CPU usage](https://man7.org/linux/man-pages/man1/top.1.html) of PD will increase by about 10% when the interval is `1ms`.
+ Default value: `50ms`
+ Minimum value: `1ms`
