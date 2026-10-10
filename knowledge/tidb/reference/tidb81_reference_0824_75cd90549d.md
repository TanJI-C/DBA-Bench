# Audit log field definitions and limitations

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/serverless-audit-logging.md`
- Source Title: `TiDB Cloud Serverless Database Audit Logging`
- Source Heading Path: `TiDB Cloud Serverless Database Audit Logging (Beta) > Audit logging fields > SQL statement information | TiDB Cloud Serverless Database Audit Logging (Beta) > Audit logging fields > Connection information | TiDB Cloud Serverless Database Audit Logging (Beta) > Audit logging fields > Audit operation information | TiDB Cloud Serverless Database Audit Logging (Beta) > Audit logging limitations`
- Source Line Ranges: `190-230`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`, `sql`
- Topic Tags: `audit-logging`, `log-fields`, `sql-statements`, `connection-metadata`, `audit-operations`, `limitations`, `cli`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0824_75cd90549d`
- Source ID: `tidb-docs-8.1:tidb-cloud/serverless-audit-logging.md#sql-statement-information`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `eb8d4053617002f6a637fda0677fad04f148bb0cccb3da853c686487615b2d14`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-audit-logging#sql-statement-information
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/serverless-audit-logging.md

## Retrieval Guidance

- Use When: Use this chunk when identifying which audit log fields appear for QUERY, CONNECTION, or AUDIT event classes in TiDB Cloud Serverless Database Audit Logging (Beta), or when checking the stated audit logging limitations.
- Retrieval Keywords: TiDB Cloud Serverless Database Audit Logging (Beta), audit logging fields, QUERY, CONNECTION, AUDIT, CURRENT_DB, SQL_TEXT, EXECUTE_PARAMS, AFFECTED_ROWS, CONNECTION_TYPE, PID, SERVER_VERSION, SSL_VERSION, HOST_IP, HOST_PORT, CLIENT_IP, CLIENT_PORT, AUDIT_OP_TARGET, AUDIT_OP_ARGS, audit log redaction, QUERY_DML, DISCONNECT, TiDB Cloud CLI, TIME field, sequential order of audit logs
- Follow-up Guidance: The source also states that TiDB Cloud Serverless does not guarantee the sequential order of audit logs and that the `TIME` field can be used to sort logs chronologically.
- Classification Note: This is reference content because it enumerates audit log field definitions for specific event classes and lists explicit audit logging limitations in TiDB Cloud Serverless.

## Official Source Content

### SQL statement information

When the event class is `QUERY` or a subclass of `QUERY`, the audit logs contain the following information:

| Field          | Description                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------------|
| CURRENT_DB     | The name of the current database.                                                                              |
| SQL_TEXT       | The executed SQL statements. If audit log redaction is enabled, the redacted SQL statements are recorded.     |
| EXECUTE_PARAMS | The parameters for the `EXECUTE` statements. Recorded only when the event classes include `EXECUTE` and redaction is disabled. |
| AFFECTED_ROWS  | The number of affected rows of the SQL statements. Recorded only when the event classes include `QUERY_DML`.    |
### Connection information

When the event class is `CONNECTION` or a subclass of `CONNECTION`, the audit logs contain the following information:

| Field           | Description                                                                                   |
|-----------------|-----------------------------------------------------------------------------------------------|
| CURRENT_DB      | The name of the current database. When the event classes include DISCONNECT, this information is not recorded. |
| CONNECTION_TYPE | The type of connection, including Socket, UnixSocket, and SSL/TLS.                                 |
| PID             | The process ID of the current connection.                                                          |
| SERVER_VERSION  | The current version of the connected TiDB server.                                                  |
| SSL_VERSION     | The current version of SSL in use.                                                                 |
| HOST_IP         | The current IP address of the connected TiDB server.                                              |
| HOST_PORT       | The current port of the connected TiDB server.                                                     |
| CLIENT_IP       | The current IP address of the client.                                                             |
| CLIENT_PORT     | The current port of the client.                                                                    |
### Audit operation information

When the event class is `AUDIT` or a subclass of `AUDIT`, the audit logs contain the following information:

| Field          | Description                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------------|
| AUDIT_OP_TARGET| The objects of the setting related to TiDB database auditing. |
| AUDIT_OP_ARGS  | The arguments of the setting related to TiDB database auditing. |
## Audit logging limitations

- Audit logging is only available via TiDB Cloud CLI at present.
- Audit logs can only be stored in TiDB Cloud at present.
- TiDB Cloud Serverless does not guarantee the sequential order of audit logs, which means you might have to review all log files to view the latest events. To sort the logs chronologically, you can use the `TIME` field in the audit logs.
