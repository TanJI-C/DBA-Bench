# TiProxy security behavior and connection limitations

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiproxy/tiproxy-overview.md`
- Source Title: `TiProxy Overview`
- Source Heading Path: `TiProxy Overview > Security | TiProxy Overview > Limitations`
- Source Line Ranges: `149-185`
- Source Scope: `shared`
- Primary Component: `shared`
- Related Components: `tidb`
- Topic Tags: `tls`, `authentication`, `backend-tls`, `client-connections`, `connection-migration`, `session-limitations`, `failover`, `compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0964_10eae8d254`
- Source ID: `tidb-docs-8.1:tiproxy/tiproxy-overview.md#security`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d5c039a5ecf8afecbebff9c4416e2b41ef70ceb77ddc5fbeb8f6c533bd3f6327`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiproxy/tiproxy-overview#security
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiproxy/tiproxy-overview.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about TiProxy TLS behavior, differences from TiDB security reporting, or scenarios where TiProxy cannot keep or migrate client connections.
- Retrieval Keywords: TiProxy Security, TiProxy Limitations, security.server-tls, security.require-backend-tls, security.sql-tls, TLS connection between client and TiProxy, TLS connection between TiProxy and TiDB server, STATUS, SHOW STATUS, certificate-based authentication, wait_timeout, graceful-wait-before-shutdown, TiDB is offline unexpectedly, TiProxy performs scaling in, upgrade, or restart, cursor, local temporary table, user-level lock, table lock, prepared statement is invalid, session-level execution plan binding, user deleted or username changed
- Follow-up Guidance: The content also lists incompatible behaviors such as `STATUS` versus `SHOW STATUS` TLS information and that TiProxy does not support certificate-based authentication.
- Classification Note: This is reference content because it specifies exact TLS rules, incompatibilities, and connection retention or migration limitations for TiProxy.

## Official Source Content

## Security

TiProxy provides TLS connections. The TLS connection between the client and TiProxy is enabled according to the following rules:

- If the [`security.server-tls`](https://docs.pingcap.com/tidb/stable/tiproxy/tiproxy-configuration#server-tls) configuration of TiProxy is set to not use TLS connection, the TLS connection between the client and TiProxy is not enabled regardless of whether the client enables TLS connection.
- If the [`security.server-tls`](https://docs.pingcap.com/tidb/stable/tiproxy/tiproxy-configuration#server-tls) configuration of TiProxy is set to use TLS connection, the TLS connection between the client and TiProxy is enabled only when the client enables TLS connection.

The TLS connection between TiProxy and TiDB server is enabled according to the following rules:

- If TiProxy's [`security.require-backend-tls`](https://docs.pingcap.com/tidb/stable/tiproxy/tiproxy-configuration#require-backend-tls) is set to `true`, TiProxy and TiDB server always enable TLS connection regardless of whether the client enables TLS connection. If TiProxy's [`security.sql-tls`](https://docs.pingcap.com/tidb/stable/tiproxy/tiproxy-configuration#sql-tls) is set to not use TLS or TiDB server does not configure TLS certificate, the client reports an error.
- If TiProxy's [`security.require-backend-tls`](https://docs.pingcap.com/tidb/stable/tiproxy/tiproxy-configuration#require-backend-tls) is set to `false`, TiProxy's [`security.sql-tls`](https://docs.pingcap.com/tidb/stable/tiproxy/tiproxy-configuration#sql-tls) is configured with TLS and TiDB server is configured with a TLS certificate, TiProxy and TiDB server only enable TLS connection when the client enables TLS connection.
- If TiProxy's [`security.require-backend-tls`](https://docs.pingcap.com/tidb/stable/tiproxy/tiproxy-configuration#require-backend-tls) is set to `false`, TiProxy's [`security.sql-tls`](https://docs.pingcap.com/tidb/stable/tiproxy/tiproxy-configuration#sql-tls) is set to not use TLS or TiDB server does not configure a TLS certificate, TiProxy and TiDB server do not enable TLS connection.

TiProxy has the following behaviors incompatible with TiDB:

- The `STATUS` and `SHOW STATUS` statements might return different TLS information. The `STATUS` statement returns the TLS information between the client and TiProxy, while the `SHOW STATUS` statement returns the TLS information between TiProxy and TiDB server.
- TiProxy does not support [certificate-based authentication](https://docs.pingcap.com/tidb/stable/certificate-authentication). Otherwise, the client might fail to log in because the TLS certificate between the client and TiProxy is different from that between TiProxy and TiDB server, and TiDB server verifies the TLS certificate based on the TLS certificate on TiProxy.
## Limitations

TiProxy cannot keep the client connection in the following scenarios:

- TiDB is offline unexpectedly. TiProxy only keeps the client connection when the TiDB server is offline or restarted as planned, and does not support failover of the TiDB server.
- TiProxy performs scaling in, upgrade, or restart. Once TiProxy is offline, the client connection is broken.
- TiDB actively disconnects the connection. For example, when a session does not send a request for a period of time longer than `wait_timeout`, TiDB actively disconnects the connection, and TiProxy also disconnects the client connection.

TiProxy cannot migrate connections in the following scenarios, and thus cannot keep the client connection or achieve load balancing:

- The duration of a single statement or a single transaction exceeds the [`graceful-wait-before-shutdown`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#graceful-wait-before-shutdown-new-in-v50) configured on the TiDB server.
- The session uses the cursor to read data, and the cursor is not closed or the data is not read within the [`graceful-wait-before-shutdown`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#graceful-wait-before-shutdown-new-in-v50) configured on the TiDB server.
- The session creates a [local temporary table](https://docs.pingcap.com/tidb/stable/temporary-tables#local-temporary-tables).
- The session holds a [user-level lock](https://docs.pingcap.com/tidb/stable/functions-and-operators/locking-functions).
- The session holds a [table lock](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-lock-tables-and-unlock-tables).
- The session creates a [prepared statement](https://docs.pingcap.com/tidb/stable/develop/dev-guide-prepared-statement), and the prepared statement is invalid. For example, the table related to the prepared statement is dropped after the prepared statement is created.
- The session creates a session-level [execution plan binding](https://docs.pingcap.com/tidb/stable/sql-plan-management#sql-binding), and the binding is invalid. For example, the table related to the binding is dropped after the binding is created.
- After the session is created, the user used by the session is deleted or the username is changed.
