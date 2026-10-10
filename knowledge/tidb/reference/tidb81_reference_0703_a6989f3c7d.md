# Server status variables reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/status-variables.md`
- Source Title: `Server Status Variables`
- Source Heading Path: `Server Status Variables | Server Status Variables > Variable reference | Server Status Variables > Variable reference > Compression | Server Status Variables > Variable reference > Compression_algorithm | Server Status Variables > Variable reference > Compression_level | Server Status Variables > Variable reference > Ssl_cipher | Server Status Variables > Variable reference > Ssl_cipher_list | Server Status Variables > Variable reference > Ssl_server_not_after | Server Status Variables > Variable reference > Ssl_server_not_before | Server Status Variables > Variable reference > Ssl_verify_mode | Server Status Variables > Variable reference > Ssl_version | Server Status Variables > Variable reference > Uptime | Server Status Variables > Variable reference > ddl_schema_version | Server Status Variables > Variable reference > last_plan_binding_update_time <span class="version-mark">New in v5.2.0</span> | Server Status Variables > Variable reference > server_id | Server Status Variables > Variable reference > tidb_gc_last_run_time | Server Status Variables > Variable reference > tidb_gc_leader_desc | Server Status Variables > Variable reference > tidb_gc_leader_lease | Server Status Variables > Variable reference > tidb_gc_leader_uuid | Server Status Variables > Variable reference > tidb_gc_safe_point`
- Source Line Ranges: `5-122`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `status-variables`, `show-global-status`, `show-session-status`, `flush-status`, `mysql-protocol`, `compression`, `tls`, `uptime`, `ddl-schema`, `plan-binding`, `server-id`, `gc`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0703_a6989f3c7d`
- Source ID: `tidb-docs-8.1:status-variables.md#server-status-variables`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5cf9939037079e4458438b5422a781f8c581e3588d7457a996dce8f6342fa1b0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/status-variables#server-status-variables
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/status-variables.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB server status variables available through SHOW GLOBAL STATUS or SHOW SESSION STATUS, including MySQL protocol compression, TLS status, uptime, DDL schema version, plan binding update time, server UUID, and GC status fields.
- Retrieval Keywords: Server Status Variables, SHOW GLOBAL STATUS, SHOW SESSION STATUS, FLUSH STATUS, Compression, Compression_algorithm, Compression_level, Ssl_cipher, Ssl_cipher_list, Ssl_server_not_after, Ssl_server_not_before, Ssl_verify_mode, Ssl_version, Uptime, ddl_schema_version, last_plan_binding_update_time, server_id, tidb_gc_last_run_time, tidb_gc_leader_desc, tidb_gc_leader_lease, tidb_gc_leader_uuid, tidb_gc_safe_point, MySQL Protocol uses compression, TLS Cipher that is in use, The UUID of the server, GC leader, GC safe point
- Follow-up Guidance: The content points to SHOW GLOBAL STATUS, SHOW SESSION STATUS, and FLUSH STATUS as the related SQL statements for retrieving or resetting status information.
- Classification Note: This is a reference chunk because it enumerates server status variable names with their scope, type, and meaning for TiDB and SQL status commands.

## Official Source Content

# Server Status Variables

Server status variables provide information about the global status of the server and the status of the current session in TiDB. Most of these variables are designed to be compatible with MySQL.

You can retrieve the global status using the [SHOW GLOBAL STATUS](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-status) command, and the status of the current session using the [SHOW SESSION STATUS](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-status) command. 

Additionally, the [FLUSH STATUS](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-flush-status) command is supported for MySQL compatibility.
## Variable reference
### Compression

- Scope: SESSION
- Type: Boolean
- Indicates if the MySQL Protocol uses compression or not.
### Compression_algorithm

- Scope: SESSION
- Type: String
- Indicates the compression algorithm that is used for the MySQL Protocol.
### Compression_level

- Scope: SESSION
- Type: Integer
- The compression level that is used for the MySQL Protocol.
### Ssl_cipher

- Scope: SESSION | GLOBAL
- Type: String
- TLS Cipher that is in use.
### Ssl_cipher_list

- Scope: SESSION | GLOBAL
- Type: String
- The list of TLS Ciphers that the server supports.
### Ssl_server_not_after

- Scope: SESSION | GLOBAL
- Type: Date
- The expiration date of the X.509 certificate of the server that is used for TLS connections.
### Ssl_server_not_before

- Scope: SESSION | GLOBAL
- Type: String
- The start date of the X.509 certificate of the server that is used for TLS connections.
### Ssl_verify_mode

- Scope: SESSION | GLOBAL
- Type: Integer
- The TLS verification mode bitmask.
### Ssl_version

- Scope: SESSION | GLOBAL
- Type: String
- The version of the TLS protocol that is used
### Uptime

- Scope: SESSION | GLOBAL
- Type: Integer
- Uptime of the server in seconds.
### ddl_schema_version

- Scope: SESSION | GLOBAL
- Type: Integer
- The version of the DDL schema that is used.
### last_plan_binding_update_time New in v5.2.0

- Scope: SESSION
- Type: Timestamp
- The time and date of the last plan binding update.
### server_id

- Scope: SESSION | GLOBAL
- Type: String
- The UUID of the server.
### tidb_gc_last_run_time

- Scope: SESSION | GLOBAL
- Type: String
- The timestamp of the last run of [GC](https://docs.pingcap.com/tidb/stable/garbage-collection-overview).
### tidb_gc_leader_desc

- Scope: SESSION | GLOBAL
- Type: String
- Information about [GC](https://docs.pingcap.com/tidb/stable/garbage-collection-overview) leader, including the hostname and process id (pid).
### tidb_gc_leader_lease

- Scope: SESSION | GLOBAL
- Type: String
- The timestamp of the [GC](https://docs.pingcap.com/tidb/stable/garbage-collection-overview) lease.
### tidb_gc_leader_uuid

- Scope: SESSION | GLOBAL
- Type: String
- The UUID of the [GC](https://docs.pingcap.com/tidb/stable/garbage-collection-overview) leader.
### tidb_gc_safe_point

- Scope: SESSION | GLOBAL
- Type: String
- The timestamp of the [GC](https://docs.pingcap.com/tidb/stable/garbage-collection-overview) safe point.
