# ALTER INSTANCE RELOAD TLS syntax and behavior

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-alter-instance.md`
- Source Title: `ALTER INSTANCE`
- Source Heading Path: `ALTER INSTANCE | ALTER INSTANCE > RELOAD TLS | ALTER INSTANCE > Syntax diagram | ALTER INSTANCE > Example | ALTER INSTANCE > MySQL compatibility | ALTER INSTANCE > See also`
- Source Line Ranges: `5-68`
- Source Scope: `all`
- Primary Component: `sql`
- Related Components: `tidb`, `cloud`
- Topic Tags: `alter instance`, `reload tls`, `tls certificates`, `ssl configuration`, `syntax`, `mysql compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0523_9ecefdcb67`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-alter-instance.md#alter-instance`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7ecd76ab26aa7ce0fb86bc45aba7bc8e437971e30488c92d63bb6e688f35e10e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-instance#alter-instance
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-alter-instance.md

## Retrieval Guidance

- Use When: Use this when looking for the syntax and behavior of `ALTER INSTANCE RELOAD TLS`, including how TiDB reloads `ssl-cert`, `ssl-key`, and `ssl-ca` from the original configuration path and what `NO ROLLBACK ON ERROR` means.
- Retrieval Keywords: ALTER INSTANCE, ALTER INSTANCE RELOAD TLS, RELOAD TLS, NO ROLLBACK ON ERROR, ssl-cert, ssl-key, ssl-ca, original configuration path, The connection established before this statement execution is not affected, MySQL compatibility
- Follow-up Guidance: The source also points to `Enable TLS Between TiDB Clients and Servers` for related TLS setup information.
- Classification Note: This is reference content because it defines the supported `ALTER INSTANCE` clause, gives the EBNF syntax, an example SQL statement, and the exact runtime behavior and compatibility notes from the official documentation.

## Official Source Content

# ALTER INSTANCE

The `ALTER INSTANCE` statement is used to make changes to a single TiDB instance. Currently, TiDB only supports the `RELOAD TLS` clause.

> **Note:**
>
> [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) can automatically refresh the TLS certificate, so this feature is not applicable to [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.
## RELOAD TLS

You can execute the `ALTER INSTANCE RELOAD TLS` statement to reload the certificate ([`ssl-cert`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#ssl-cert)), the key ([`ssl-key`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#ssl-key)), and the CA ([`ssl-ca`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#ssl-ca)) from the original configuration path.

You can execute the `ALTER INSTANCE RELOAD TLS` statement to reload the certificate ([`ssl-cert`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#ssl-cert)), the key ([`ssl-key`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#ssl-key)), and the CA ([`ssl-ca`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#ssl-ca)) from the original configuration path.

The newly loaded certificate, key, and CA take effect on the connection that is established after the statement is successfully executed. The connection established before this statement execution is not affected.

When an error occurs during reloading, by default, this error message is returned and the previous key and certificate continue to be used. However, if you have added the optional `NO ROLLBACK ON ERROR`, when an error occurs during reloading, the error is not returned, and the subsequent requests are handled with the TLS security connection disabled.
## Syntax diagram

**AlterInstanceStmt:**

```ebnf+diagram
AlterInstanceStmt ::=
    'ALTER' 'INSTANCE' InstanceOption

InstanceOption ::=
    'RELOAD' 'TLS' ('NO' 'ROLLBACK' 'ON' 'ERROR')?
```
## Example

```sql
ALTER INSTANCE RELOAD TLS;
```
## MySQL compatibility

The `ALTER INSTANCE RELOAD TLS` statement only supports reloading from the original configuration path. It does not support dynamically modifying the loading path or dynamically enabling the TLS encrypted connection feature when TiDB is started. This feature is disabled by default when you restart TiDB.
## See also

[Enable TLS Between TiDB Clients and Servers](https://docs.pingcap.com/tidb/stable/enable-tls-between-clients-and-servers).

[Enable TLS Between TiDB Clients and Servers](https://docs.pingcap.com/tidb/stable/enable-tls-between-clients-and-servers).
