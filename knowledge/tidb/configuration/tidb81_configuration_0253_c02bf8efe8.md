# Enable and manage audit logging filter rules

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/serverless-audit-logging.md`
- Source Title: `TiDB Cloud Serverless Database Audit Logging`
- Source Heading Path: `TiDB Cloud Serverless Database Audit Logging (Beta) | TiDB Cloud Serverless Database Audit Logging (Beta) > Enable audit logging | TiDB Cloud Serverless Database Audit Logging (Beta) > Manage audit logging filter rules | TiDB Cloud Serverless Database Audit Logging (Beta) > Manage audit logging filter rules > Create a filter rule | TiDB Cloud Serverless Database Audit Logging (Beta) > Manage audit logging filter rules > Update a filter rule | TiDB Cloud Serverless Database Audit Logging (Beta) > Manage audit logging filter rules > Delete a filter rule`
- Source Line Ranges: `5-108`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `audit-logging`, `enablement`, `cli`, `filter-rules`, `event-classes`, `user-filters`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0253_c02bf8efe8`
- Source ID: `tidb-docs-8.1:tidb-cloud/serverless-audit-logging.md#tidb-cloud-serverless-database-audit-logging-beta`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c820b97322077f4ae73ba85674b80a48e406ce9111d1ce259cef31d77405117b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-audit-logging#tidb-cloud-serverless-database-audit-logging-beta
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/serverless-audit-logging.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs TiDB Cloud Serverless audit logging enablement commands or wants to create, update, disable, or delete audit logging filter rules and match event classes, users, tables, or status codes.
- Retrieval Keywords: TiDB Cloud Serverless Database Audit Logging (Beta), ticloud serverless audit-log config -c <cluster-id> --enabled, ticloud serverless audit-log config -c <cluster-id> --enabled=false, ticloud serverless audit-log filter create, ticloud serverless audit-log filter update, ticloud serverless audit-log filter delete, users, filters, classes, tables, statusCodes, QUERY, EXECUTE, CONNECTION, TRANSACTION, QUERY_DML, QUERY_DDL, AUDIT, AUDIT_FUNC_CALL, %@%, --rule
- Follow-up Guidance: The source also notes that enabling audit logging alone does not generate audit logs and that you need to configure filters to specify what events to log.
- Classification Note: This is classified as configuration because the content defines how to enable or disable audit logging and manage CLI-based filter rule settings for TiDB Cloud Serverless.

## Official Source Content

# TiDB Cloud Serverless Database Audit Logging (Beta)

TiDB Cloud Serverless provides you with a database audit logging feature to record a history of user access details (such as any SQL statements executed) in logs.

> **Note:**
>
> Currently, the database audit logging feature is only available upon request. To request this feature, click **?** in the lower-right corner of the [TiDB Cloud console](https://tidbcloud.com) and click **Request Support**. Then, fill in "Apply for TiDB Cloud Serverless database audit logging" in the **Description** field and click **Submit**.

To assess the effectiveness of user access policies and other information security measures of your organization, it is a security best practice to conduct a periodic analysis of the database audit logs.

The audit logging feature is disabled by default. To audit a cluster, you need to enable audit logging for it.
## Enable audit logging

To enable audit logging for a TiDB Cloud Serverless cluster, use the [TiDB Cloud CLI](https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-auditlog-config).

```shell
ticloud serverless audit-log config -c <cluster-id> --enabled
```

To disable audit logging for a TiDB Cloud Serverless cluster, use the [TiDB Cloud CLI](https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-auditlog-config).

```shell
ticloud serverless audit-log config -c <cluster-id> --enabled=false
```

> **Note:**
>
> Only enabling audit logging will not generate audit logs. You need to configure filters to specify what events to log. For more information, see [Manage audit logging filter rules](#manage-audit-logging-filter-rules).
## Manage audit logging filter rules

To filter the audit logging, you need to create a filter rule to specify which events to log. You can use the [TiDB Cloud CLI](https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-auditlog-filter-create) to manage the filter rules.

The filter rule contains the following fields:

- `users`: A list of user names to filter audit events. You can use the wildcard `%` to match any user name.
- `filters`: A list of filter objects. Each filter object can contain the following fields:

    - `classes`: A list of event classes to filter audit events. For example, `["QUERY", "EXECUTE"]`.
    - `tables`: A list of table filters. For more information, see [Table filters].
    - `statusCodes`: A list of status codes to filter audit events. `1` means success, `0` means failure.

Here is the summary of all event classes in database audit logging:

| Event Class   | Description                                                                                      | Parent-class   |
|---------------|--------------------------------------------------------------------------------------------------|---------------|
| CONNECTION    | Record all operations related to connections, such as handshaking, connections, disconnections, connection reset, and changing users | -             |
| CONNECT       | Record all operations of the handshaking in connections                                          | CONNECTION    |
| DISCONNECT    | Record all operations of the disconnections                                                      | CONNECTION    |
| CHANGE_USER   | Record all operations of changing users                                                          | CONNECTION    |
| QUERY         | Record all operations of SQL statements, including all errors about querying and modifying data  | -             |
| TRANSACTION   | Record all operations related to transactions, such as `BEGIN`, `COMMIT`, and `ROLLBACK`               | QUERY         |
| EXECUTE       | Record all operations of the `EXECUTE` statements                                                  | QUERY         |
| QUERY_DML     | Record all operations of the DML statements, including `INSERT`, `REPLACE`, `UPDATE`, `DELETE`, and `LOAD DATA` | QUERY     |
| INSERT        | Record all operations of the `INSERT` statements                                                   | QUERY_DML     |
| REPLACE       | Record all operations of the `REPLACE` statements                                                  | QUERY_DML     |
| UPDATE        | Record all operations of the `UPDATE` statements                                                   | QUERY_DML     |
| DELETE        | Record all operations of the `DELETE` statements                                                   | QUERY_DML     |
| LOAD DATA     | Record all operations of the `LOAD DATA` statements                                                | QUERY_DML     |
| SELECT        | Record all operations of the `SELECT` statements                                                   | QUERY         |
| QUERY_DDL          | Record all operations of the DDL statements                                                      | QUERY               |
| AUDIT              | Record all operations related to setting TiDB database auditing, including setting system variables and calling system functions | -                   |
| AUDIT_FUNC_CALL    | Record all operations of calling system functions related to TiDB database auditing               | AUDIT               |
### Create a filter rule

To create a filter rule that captures all audit logs, run the following command:

```shell
ticloud serverless audit-log filter create --cluster-id <cluster-id> --name <rule-name> --rule '{"users":["%@%"],"filters":[{}]}'
```

To create a filter rule that filters ALL EXECUTE events, run the following command:

```shell
ticloud serverless audit-log filter create --cluster-id <cluster-id> --name <rule-name> --rule '{"users":["%@%"],"filters":[{"classes":["EXECUTE"]]}'
```
### Update a filter rule

To disable a filter rule, run the following command:

```shell
ticloud serverless audit-log filter update --cluster-id <cluster-id> --name <rule-name> --enabled=false
```

To update a filter rule, run the following command:

```shell
ticloud serverless audit-log filter update --cluster-id <cluster-id> --name <rule-name> --rule '{"users":["%@%"],"filters":[{"classes":["QUERY"],"tables":["test.t"]}]}'
```

Note that you need to pass the complete `--rule` field when updating.
### Delete a filter rule

To delete a filter rule, run the following command:

```shell
ticloud serverless audit-log filter delete --cluster-id <cluster-id> --name <rule-name>
```
