# MySQL or TiDB sink URI and downstream permissions

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-sink-to-mysql.md`
- Source Title: `Replicate Data to MySQL-compatible Databases`
- Source Heading Path: `Replicate Data to MySQL-compatible Databases > Configure sink URI for MySQL or TiDB | Replicate Data to MySQL-compatible Databases > Permissions required for the downstream database user`
- Source Line Ranges: `39-116`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `tidb`
- Topic Tags: `sink-uri`, `mysql-sink`, `tidb-sink`, `connection-parameters`, `ssl`, `timeouts`, `safe-mode`, `batch-dml`, `permissions`, `read-only-mode`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0190_ba97bff58c`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-sink-to-mysql.md#configure-sink-uri-for-mysql-or-tidb`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b800497174f774be00ce59560bddd9439f26fd10d80291a2f22e6daf35ebc3eb`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-sink-to-mysql#configure-sink-uri-for-mysql-or-tidb
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-sink-to-mysql.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the MySQL or TiDB sink URI format, supported query parameters, password encoding note, or required downstream permissions for replication.
- Retrieval Keywords: Configure sink URI for MySQL or TiDB, mysql://root:123456@127.0.0.1:3306, [scheme]://[userinfo@][host]:[port][/path]?[query_parameters], worker-count, cache-prep-stmts, multi-stmt-enable, max-txn-row, max-multi-update-row, max-multi-update-row-size, ssl-ca, ssl-cert, ssl-key, time-zone, transaction-atomicity, batch-dml-enable, read-timeout, write-timeout, timeout, tidb-txn-mode, safe-mode, Base64, URI Encoder, Permissions required for the downstream database user, Select, Index, Insert, Update, Delete, Create, Drop, Alter, Create View, RECOVER TABLE, Super, RESTRICTED_REPLICA_WRITER_ADMIN, read-only mode
- Follow-up Guidance: The source also states that special characters in the sink URI must be escaped and that additional permissions are required for RECOVER TABLE replication or when the downstream TiDB cluster has read-only mode enabled.
- Classification Note: This is classified as a configuration chunk because it defines sink URI structure, configurable connection parameters, and downstream user permission requirements.

## Official Source Content

## Configure sink URI for MySQL or TiDB

Sink URI is used to specify the connection information of the TiCDC target system. The format is as follows:

```
[scheme]://[userinfo@][host]:[port][/path]?[query_parameters]
```

> **Note:**
>
> `/path` is not used for the MySQL sink.

Sample configuration for MySQL:

```shell
--sink-uri="mysql://root:123456@127.0.0.1:3306"
```

The following are descriptions of sink URI parameters and parameter values that can be configured for MySQL or TiDB:

| Parameter/Parameter value    | Description                                             |
| :------------ | :------------------------------------------------ |
| `root`        | The username of the downstream database. To replicate data to TiDB or other MySQL-compatible databases, make sure that the downstream database user has [certain permissions](#permissions-required-for-the-downstream-database-user).                             |
| `123456`       | The password of the downstream database (can be encoded using Base64).                                      |
| `127.0.0.1`    | The IP address of the downstream database.                               |
| `3306`         | The port for the downstream database.                                 |
| `worker-count` | The number of SQL statements that can be concurrently executed to the downstream (optional, the default value is `16`, and the maximum value is `1024`). |
| `cache-prep-stmts` | Controls whether to use prepared statements when executing SQL in the downstream and enable prepared statement cache on the client side (optional, `true` by default). |
| `multi-stmt-enable` | Controls whether the SQL statements executed downstream support multiple SQL statements separated by semicolons (optional, the default value is `true`). If it is set to `false`, each SQL statement is executed as a separate transaction. If it is set to `true`, `cache-prep-stmts` does not take effect. |
| `max-txn-row` | The batch size of SQL statements executed to the downstream (optional, the default value is `256`, and the maximum value is `2048`). |
| `max-multi-update-row` | The batch size of `UPDATE ROWS` SQL statements executed to the downstream when batch write (`batch-dml-enable`) is enabled, always less than `max-txn-row` (optional, the default value is `40`, and the maximum value is `256`). |
| `max-multi-update-row-size` | When batch write (`batch-dml-enable`) is enabled, this parameter controls the batch processing size (in bytes) for `UPDATE ROWS` SQL statements executed to the downstream. If the average size of a single row exceeds this threshold, each row is executed as an independent SQL statement (optional, the default value is `1024`, and the maximum value is `8192`). |
| `ssl-ca` | The path of the CA certificate file needed to connect to the downstream MySQL instance (optional).  |
| `ssl-cert` | The path of the certificate file needed to connect to the downstream MySQL instance (optional). |
| `ssl-key` | The path of the certificate key file needed to connect to the downstream MySQL instance (optional). |
| `time-zone` | The time zone used when connecting to the downstream MySQL instance, which is effective since v4.0.8. This is an optional parameter. If this parameter is not specified, the time zone of TiCDC service processes is used. If this parameter is set to an empty value, such as `time-zone=""`, no time zone is specified when TiCDC connects to the downstream MySQL instance and the default time zone of the downstream is used. |
| `transaction-atomicity`  |  The atomicity level of a transaction. This is an optional parameter, with the default value of `none`. When the value is `table`, TiCDC ensures the atomicity of a single-table transaction. When the value is `none`, TiCDC splits the single-table transaction.  |
| `batch-dml-enable` | Enables the batch write (batch-dml) feature (optional, the default value is `true`). |
| `read-timeout` | The go-sql-driver parameter, [I/O read timeout](https://pkg.go.dev/github.com/go-sql-driver/mysql#readme-readtimeout) (optional, the default value is `2m`). |
| `write-timeout` | The go-sql-driver parameter, [I/O write timeout](https://pkg.go.dev/github.com/go-sql-driver/mysql#readme-writetimeout) (optional, the default value is `2m`). |
| `timeout` | The go-sql-driver parameter, [timeout for establishing connections](https://pkg.go.dev/github.com/go-sql-driver/mysql#readme-timeout), also known as dial timeout (optional, the default value is `2m`). |
| `tidb-txn-mode` | Specifies the [`tidb_txn_mode`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_txn_mode) environment variable (optional, the default value is `optimistic`). |
| `safe-mode` | Specifies how TiCDC handles `INSERT` and `UPDATE` statements when replicating data to the downstream. When it is `true`, TiCDC converts all upstream `INSERT` statements to `REPLACE INTO` statements, and all `UPDATE` statements to `DELETE` + `REPLACE INTO` statements. Before v6.1.3, the default value of this parameter is `true`. Starting from v6.1.3, the default value is changed to `false`. When TiCDC starts, it obtains a current timestamp `ThresholdTs`. For `INSERT` and `UPDATE` statements with `CommitTs` less than `ThresholdTs`, TiCDC converts them to `REPLACE INTO` statements and `DELETE` + `REPLACE INTO` statements respectively. For `INSERT` and `UPDATE` statements with `CommitTs` greater than or equal to `ThresholdTs`, `INSERT` statements are directly replicated to the downstream, while the behavior of `UPDATE` statements follows the [TiCDC Behavior in Splitting UPDATE Events](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-split-update-behavior). |

To encode the database password in the sink URI using Base64, use the following command:

```shell
echo -n '123456' | base64   # '123456' is the password to be encoded.
```

The encoded password is `MTIzNDU2`:

```shell
MTIzNDU2
```

> **Note:**
>
> When the sink URI contains special characters such as `! * ' ( ) ; : @ & = + $ , / ? % # [ ]`, you need to escape the special characters, for example, in [URI Encoder](https://www.urlencoder.org/).
## Permissions required for the downstream database user

To replicate data to TiDB or other MySQL-compatible databases, the downstream database user needs the following permissions:

- `Select`
- `Index`
- `Insert`
- `Update`
- `Delete`
- `Create`
- `Drop`
- `Alter`
- `Create View`

To replicate [`RECOVER TABLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-recover-table) to the downstream TiDB, the downstream database user also needs the `Super` permission.

If the downstream TiDB cluster has [read-only mode](https://docs.pingcap.com/tidb/stable/system-variables#tidb_restricted_read_only-new-in-v520) enabled, the downstream database user also needs the `RESTRICTED_REPLICA_WRITER_ADMIN` permission.
