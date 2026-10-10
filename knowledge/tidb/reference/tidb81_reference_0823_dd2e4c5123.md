# Audit log record fields and general information

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/serverless-audit-logging.md`
- Source Title: `TiDB Cloud Serverless Database Audit Logging`
- Source Heading Path: `TiDB Cloud Serverless Database Audit Logging (Beta) > Audit logging fields | TiDB Cloud Serverless Database Audit Logging (Beta) > Audit logging fields > General information`
- Source Line Ranges: `166-189`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `audit-logging`, `fields`, `schema`, `event-records`, `metadata`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0823_dd2e4c5123`
- Source ID: `tidb-docs-8.1:tidb-cloud/serverless-audit-logging.md#audit-logging-fields`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e3840067cc44e1344c1780698cbdb3a4887db5e97226636be8b05c140d78e7e3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-audit-logging#audit-logging-fields
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/serverless-audit-logging.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the field definitions for TiDB audit log records in TiDB Cloud Serverless, including general metadata and error-related fields.
- Retrieval Keywords: Audit logging fields, General information, ID, TIME, EVENT, USER, ROLES, CONNECTION_ID, TABLES, STATUS_CODE, KEYSPACE_NAME, SERVERLESS_TENANT_ID, SERVERLESS_TSERVERLESS_PROJECT_ID, SERVERLESS_CLUSTER_ID, REASON, status code 1 means success, status code 0 means failure
- Follow-up Guidance: The source says that REASON is only recorded when an error occurs during the operation.
- Classification Note: This is classified as reference because the content is a schema-style listing of audit log record fields and their meanings.

## Official Source Content

## Audit logging fields

For each database event record in audit logs, TiDB provides the following fields:
### General information

All classes of audit logs contain the following information:

| Field         | Description                                                                                   |
|---------------|-----------------------------------------------------------------------------------------------|
| ID            | The unique identifier that identifies the audit record of an operation                        |
| TIME          | The timestamp of the audit record                        |
| EVENT         | The event classes of the audit record. Multiple event types are separated by commas (`,`)        |
| USER          | The username of the audit record                                                              |
| ROLES         | The roles of the user at the time of the operation                                            |
| CONNECTION_ID | The identifier of the user's connection                                                       |
| TABLES        | The accessed tables related to this audit record                                              |
| STATUS_CODE   | The status code of the audit record. `1` means success, and `0` means failure.                       |
| KEYSPACE_NAME | The keyspace name of the audit record. |
| SERVERLESS_TENANT_ID           | The ID of the serverless tenant that the cluster belongs to. |
| SERVERLESS_TSERVERLESS_PROJECT_ID         | The ID of the serverless project that the cluster belongs to. |
| SERVERLESS_CLUSTER_ID          | The ID of the serverless cluster that the audit record belongs to. |
| REASON        | The error message of the audit record. Only recorded when an error occurs during the operation. |
