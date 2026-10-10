# General TiDB server configuration options and compatibility controls

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-configuration-file.md`
- Source Title: `TiDB Configuration File`
- Source Heading Path: `TiDB Configuration File > `max-index-length` | TiDB Configuration File > `table-column-count-limit` <span class="version-mark">New in v5.0</span> | TiDB Configuration File > `index-limit` <span class="version-mark">New in v5.0</span> | TiDB Configuration File > `enable-telemetry` <span class="version-mark">New in v4.0.2 and deprecated in v8.1.0</span> | TiDB Configuration File > `deprecate-integer-display-length` | TiDB Configuration File > `enable-tcp4-only` <span class="version-mark">New in v5.0</span> | TiDB Configuration File > `enable-enum-length-limit` <span class="version-mark">New in v5.0</span> | TiDB Configuration File > `graceful-wait-before-shutdown` <span class="version-mark">New in v5.0</span> | TiDB Configuration File > `enable-global-kill` <span class="version-mark">New in v6.1.0</span> | TiDB Configuration File > `enable-32bits-connection-id` <span class="version-mark">New in v7.3.0</span> | TiDB Configuration File > `initialize-sql-file` <span class="version-mark">New in v6.6.0</span> | TiDB Configuration File > `enable-forwarding` <span class="version-mark">New in v5.0.0</span> | TiDB Configuration File > `enable-table-lock` <span class="version-mark">New in v4.0.0</span> | TiDB Configuration File > `labels``
- Source Line Ranges: `155-272`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `operator`, `pd`, `tikv`, `tiup`
- Topic Tags: `limits`, `compatibility`, `telemetry`, `networking`, `shutdown`, `global-kill`, `connection-id`, `bootstrap-sql`, `forwarding`, `table-lock`, `labels`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0317_7181e9bbc4`
- Source ID: `tidb-docs-8.1:tidb-configuration-file.md#max-index-length`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `35e06aec0103e1fadc476e04d1408585c97ad236ae01bacc63e0e37194086e35`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-configuration-file#max-index-length
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-configuration-file.md

## Retrieval Guidance

- Use When: Use this chunk when searching for TiDB configuration items that control compatibility limits, shutdown behavior, connection killing, bootstrap SQL, forwarding, table locks, telemetry, networking, or server labels.
- Retrieval Keywords: max-index-length, table-column-count-limit, index-limit, enable-telemetry, deprecate-integer-display-length, enable-tcp4-only, enable-enum-length-limit, graceful-wait-before-shutdown, enable-global-kill, enable-32bits-connection-id, initialize-sql-file, enable-forwarding, enable-table-lock, labels, KILL, KILL TIDB, LOCK TABLES, UNLOCK TABLES, Control+C, 32-bit connection ID, Global Kill, TCP4 only, ENUM element length, SET element length, initialize SQL script, server labels, zone label, group label
- Follow-up Guidance: The content also points to related topics such as the `KILL` statement, `LOCK TABLES` and `UNLOCK TABLES`, `txn_scope`, Follower read, `TimeoutStopSec=`, TiUP Cluster `--wait-timeout`, and Kubernetes `terminationGracePeriodSeconds`.
- Classification Note: This chunk is classified as configuration because it defines TiDB server configuration options, default values, ranges, warnings, and compatibility behavior for multiple features.

## Official Source Content

### `max-index-length`

- Sets the maximum allowable length of the newly created index.
- Default value: `3072`
- Unit: byte
- Range: `[3072, 3072*4]`
- Compatibility:
    - MySQL: the maximum index length is fixed at 3072 bytes.
    - Earlier versions of TiDB:
        - v3.0.7 and earlier: the maximum index length is fixed at 3072 × 4 bytes.
        - v3.0.8 ~ v3.0.10: the maximum index length is fixed at 3072 bytes.
    - v3.0.11 and later versions: TiDB introduces the `max-index-length` configuration item to ensure compatibility with different TiDB versions and with MySQL.
### `table-column-count-limit` New in v5.0

- Sets the limit on the number of columns in a single table.
- Default value: `1017`
- Currently, the valid value range is `[1017, 4096]`.
### `index-limit` New in v5.0

- Sets the limit on the number of indexes in a single table.
- Default value: `64`
- Currently, the valid value range is `[64, 512]`.
### `enable-telemetry` New in v4.0.2 and deprecated in v8.1.0

> **Warning:**
>
> Starting from v8.1.0, the telemetry feature in TiDB is removed, and this configuration item is no longer functional. It is retained solely for compatibility with earlier versions.

- Before v8.1.0, this configuration item controls whether to enable telemetry collection in a TiDB instance.
- Default value: `false`
### `deprecate-integer-display-length`

- Deprecates the display width for integer types when this configuration item is set to `true`.
- Default value: `false`
### `enable-tcp4-only` New in v5.0

- Enables or disables listening on TCP4 only.
- Default value: `false`
- Enabling this option is useful when TiDB is used with LVS for load balancing because the [real client IP from the TCP header](https://github.com/alibaba/LVS/tree/master/kernel/net/toa) can be correctly parsed by the "tcp4" protocol.
### `enable-enum-length-limit` New in v5.0

+ Determines whether to limit the maximum length of a single `ENUM` element and a single `SET` element.
+ Default value: `true`
+ When this configuration value is `true`, the maximum length of a single `ENUM` element and a single `SET` element is 255 characters, which is compatible with [MySQL 8.0](https://dev.mysql.com/doc/refman/8.0/en/string-type-syntax.html). When this configuration value is `false`, there is no limit on the length of a single element, which is compatible with TiDB (earlier than v5.0).
### `graceful-wait-before-shutdown` New in v5.0

- Specifies the number of seconds that TiDB waits when you shut down the server, which allows the clients to disconnect.
- Default value: `0`
- When TiDB is waiting for shutdown (in the grace period), the HTTP status will indicate a failure, which allows the load balancers to reroute traffic.

> **Note:**
>
> The duration that TiDB waits before shutting down the server is also affected by the following parameters:
>
> - When you use a platform that employs SystemD, the default stop timeout is 90 seconds. If you need a longer timeout, you can set [`TimeoutStopSec=`](https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html#TimeoutStopSec=).
>
> - When you use the TiUP Cluster component, the default [`--wait-timeout`](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster#--wait-timeout) is 120 seconds.
>
> - When you use Kubernetes, the default [`terminationGracePeriodSeconds`](https://kubernetes.io/docs/reference/kubernetes-api/workload-resources/pod-v1/#lifecycle) is 30 seconds.
### `enable-global-kill` New in v6.1.0

+ Controls whether to enable the Global Kill (terminating queries or connections across instances) feature.
+ Default value: `true`
+ When the value is `true`, both `KILL` and `KILL TIDB` statements can terminate queries or connections across instances so you do not need to worry about erroneously terminating queries or connections. When you use a client to connect to any TiDB instance and execute the `KILL` or `KILL TIDB` statement, the statement will be forwarded to the target TiDB instance. If there is a proxy between the client and the TiDB cluster, the `KILL` and `KILL TIDB` statements will also be forwarded to the target TiDB instance for execution.
+ Starting from v7.3.0, you can terminate a query or connection using the MySQL command line <kbd>Control+C</kbd> when both `enable-global-kill` and [`enable-32bits-connection-id`](#enable-32bits-connection-id-new-in-v730) are set to `true`. For more information, see [`KILL`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-kill).
### `enable-32bits-connection-id` New in v7.3.0

+ Controls whether to enable the 32-bit connection ID feature.
+ Default value: `true`
+ When both this configuration item and [`enable-global-kill`](#enable-global-kill-new-in-v610) are set to `true`, TiDB generates 32-bit connection IDs. This enables you to terminate queries or connections by the MySQL command-line <kbd>Control+C</kbd>.

> **Warning:**
>
> When the number of TiDB instances in the cluster exceeds 2048 or the concurrent connection count of a single TiDB instance exceeds 1048576, the 32-bit connection ID space becomes insufficient and is automatically upgraded to 64-bit connection IDs. During the upgrade process, existing business and established connections are unaffected. However, subsequent new connections cannot be terminated using <kbd>Control+C</kbd> in the MySQL command-line.
### `initialize-sql-file` New in v6.6.0

+ Specifies the SQL script to be executed when the TiDB cluster is started for the first time.
+ Default value: `""`
+ All SQL statements in this script are executed with the highest privilege without any privilege check. If the specified SQL script fails to execute, the TiDB cluster might fail to start.
+ This configuration item is used to perform such operations as modifying the value of a system variable, creating a user, or granting privileges.
### `enable-forwarding` New in v5.0.0

+ Controls whether the PD client and TiKV client in TiDB forward requests to the leader via the followers in the case of possible network isolation.
+ Default value: `false`
+ If the environment might have isolated network, enabling this parameter can reduce the window of service unavailability.
+ If you cannot accurately determine whether isolation, network interruption, or downtime has occurred, using this mechanism has the risk of misjudgment and causes reduced availability and performance. If network failure has never occurred, it is not recommended to enable this parameter.
### `enable-table-lock` New in v4.0.0

> **Warning:**
>
> The table lock is an experimental feature. It is not recommended that you use it in the production environment.

+ Controls whether to enable the table lock feature.
+ Default value: `false`
+ The table lock is used to coordinate concurrent access to the same table among multiple sessions. Currently, the `READ`, `WRITE`, and `WRITE LOCAL` lock types are supported. When the configuration item is set to `false`, executing the `LOCK TABLES` or `UNLOCK TABLES` statement does not take effect and returns the "LOCK/UNLOCK TABLES is not supported" warning. For more information, see [`LOCK TABLES` and `UNLOCK TABLES`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-lock-tables-and-unlock-tables).
### `labels`

+ Specify server labels. For example, `{ zone = "us-west-1", dc = "dc1", rack = "rack1", host = "tidb1" }`.
+ Default value: `{}`

> **Note:**
>
> - In TiDB, the `zone` label is specially used to specify the zone where a server is located. If `zone` is set to a non-null value, the corresponding value is automatically used by features such as [`txn-score`](https://docs.pingcap.com/tidb/stable/system-variables#txn_scope) and [`Follower read`](https://docs.pingcap.com/tidb/stable/follower-read).
> - The `group` label has a special use in TiDB Operator. For clusters deployed using [TiDB Operator](https://docs.pingcap.com/tidb/stable/tidb-operator-overview), it is **NOT** recommended that you specify the `group` label manually.
