# Transaction timing, isolation, and TiKV read timeout variables

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/system-variables.md`
- Source Title: `System Variables`
- Source Heading Path: `System Variables > Variable reference > tikv_client_read_timeout <span class="version-mark">New in v7.4.0</span> | System Variables > Variable reference > time_zone | System Variables > Variable reference > timestamp | System Variables > Variable reference > transaction_isolation | System Variables > Variable reference > tx_isolation | System Variables > Variable reference > tx_isolation_one_shot | System Variables > Variable reference > tx_read_ts | System Variables > Variable reference > txn_scope`
- Source Line Ranges: `6129-6208`
- Source Scope: `all`
- Primary Component: `tidb`
- Related Components: `tikv`, `sql`, `cloud`
- Topic Tags: `system-variables`, `timeout`, `rpc`, `time-zone`, `timestamp`, `transaction-isolation`, `stale-read`, `session-scope`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0747_e4954d8be2`
- Source ID: `tidb-docs-8.1:system-variables.md#tikv-client-read-timeout-span-class-version-mark-new-in-v7-4-0-span`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a9cd733721cf4ac6e90a3c21fc004b28e3e77b2e59f1a087810e7e31dbd924a8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/system-variables#tikv-client-read-timeout-span-class-version-mark-new-in-v7-4-0-span
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/system-variables.md

## Retrieval Guidance

- Use When: Use this chunk when the question asks about TiDB system variables for TiKV RPC read timeout, time zone or timestamp behavior, transaction isolation aliases, stale read timestamp recording, or transaction scope settings.
- Retrieval Keywords: tikv_client_read_timeout, /*+ SET_VAR(TIKV_CLIENT_READ_TIMEOUT=N) */, TiKV RPC read request timeout, time_zone, SYSTEM, system_time_zone, timestamp, CURRENT_TIMESTAMP(), NOW(), transaction_isolation, tx_isolation, tx_isolation_one_shot, SET TRANSACTION ISOLATION LEVEL, Snapshot Isolation, tx_read_ts, Stale Read, txn_scope, global, local
- Follow-up Guidance: The content also notes that `tx_isolation` is an alias for `transaction_isolation`, `tx_isolation_one_shot`, `tx_read_ts`, and `txn_scope` are for internal operation of TiDB, and `txn_scope` is read-only for Starter and Essential clusters.
- Classification Note: This is reference content because it defines system variable scopes, defaults, ranges, allowed values, aliases, notes, and exact behavior for transaction timing, isolation, and related session settings.

## Official Source Content

### tikv_client_read_timeout New in v7.4.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `0`
- Range: `[0, 2147483647]`
- Unit: Millisecond
- You can use `tikv_client_read_timeout` to set the timeout for TiDB to send a TiKV RPC read request in a query. When a TiDB cluster is in an environment with unstable network or serious TiKV I/O latency jitter, and your application is sensitive to the latency of the SQL queries, you can set `tikv_client_read_timeout` to reduce the timeout of the TiKV RPC read requests. In this case, when a TiKV node has I/O latency jitter, TiDB can time out quickly and re-send the RPC request to the TiKV node where the next TiKV Region Peer is located. If the requests of all TiKV Region Peers time out, TiDB will retry with the default timeout (usually 40 seconds).
- You can also use the optimizer hint `/*+ SET_VAR(TIKV_CLIENT_READ_TIMEOUT=N) */` in a query to set the timeout for TiDB to send a TiKV RPC read request. If both the optimizer hint and this system variable are set, the optimizer hint takes higher priority.
- The default value `0` indicates that the default timeout (usually 40 seconds) is used.

> **Note:**
>
> - Normally, a regular query takes a few milliseconds, but occasionally when a TiKV node is in unstable network or gets I/O jitter, the query can take more than 1 second or even 10 seconds. In this case, you can set the TiKV RPC read request timeout to 100 milliseconds for a specific query by using the optimizer hint `/*+ SET_VAR(TIKV_CLIENT_READ_TIMEOUT=100) */`. In this way, even if the response of a TiKV node is slow, TiDB can quickly time out and then re-send the RPC request to the TiKV node where the next TiKV Region Peer is located. Because the probability of two TiKV nodes getting I/O jitter simultaneously is low, the query can be completed usually within a few milliseconds to 110 milliseconds.
> - Do not set too small values (for example, 1 millisecond) for `tikv_client_read_timeout`. Otherwise, the requests might time out easily when the workload of a TiDB cluster is high, and subsequent retries will further increase the load on the TiDB cluster.
> - If you need to set different timeout values for different types of queries, it is recommended to use optimizer hints.
### time_zone

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: `SYSTEM`
- This variable returns the current time zone. Values can be specified as either an offset such as '-8:00' or a named zone 'America/Los_Angeles'.
- The value `SYSTEM` means that the time zone should be the same as the system host, which is available via the [`system_time_zone`](#system_time_zone) variable.
### timestamp

- Scope: SESSION
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Float
- Default value: `0`
- Range: `[0, 2147483647]`
- A non-empty value of this variable indicates the UNIX epoch that is used as the timestamp for `CURRENT_TIMESTAMP()`, `NOW()`, and other functions. This variable might be used in data restore or replication.
### transaction_isolation

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Enumeration
- Default value: `REPEATABLE-READ`
- Possible values: `READ-UNCOMMITTED`, `READ-COMMITTED`, `REPEATABLE-READ`, `SERIALIZABLE`
- This variable sets the transaction isolation. TiDB advertises `REPEATABLE-READ` for compatibility with MySQL, but the actual isolation level is Snapshot Isolation. See [transaction isolation levels](https://docs.pingcap.com/tidb/stable/transaction-isolation-levels) for further details.
### tx_isolation

This variable is an alias for `transaction_isolation`.
### tx_isolation_one_shot

> **Note:**
>
> This variable is internally used in TiDB. You are not expected to use it.

Internally, the TiDB parser transforms the `SET TRANSACTION ISOLATION LEVEL [READ COMMITTED| REPEATABLE READ | ...]` statements to `SET @@SESSION.TX_ISOLATION_ONE_SHOT = [READ COMMITTED| REPEATABLE READ | ...]`.
### tx_read_ts

- Scope: SESSION
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: ""
- In the Stale Read scenarios, this session variable is used to help record the Stable Read timestamp value.
- This variable is used for the internal operation of TiDB. It is **NOT recommended** to set this variable.
### txn_scope

> **Note:**
>
> This variable is read-only for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

- Scope: SESSION
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: `global`
- Value options: `global` and `local`
- This variable is used to set whether the current session transaction is a global transaction or a local transaction.
- This variable is used for the internal operation of TiDB. It is **NOT recommended** to set this variable.
