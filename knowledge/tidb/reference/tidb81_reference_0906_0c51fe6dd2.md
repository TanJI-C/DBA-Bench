# Console audit log fields reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tidb-cloud-console-auditing.md`
- Source Title: `Console Audit Logging`
- Source Heading Path: `Console Audit Logging > Console audit log fields`
- Source Line Ranges: `164-185`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `audit-logging`, `fields`, `events`, `operators`, `metadata`, `schema`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0906_0c51fe6dd2`
- Source ID: `tidb-docs-8.1:tidb-cloud/tidb-cloud-console-auditing.md#console-audit-log-fields`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ce378b44732e1cbe12d6f034b078ae90729c85679f7e3a52b330eab3f18ddac0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-console-auditing#console-audit-log-fields
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tidb-cloud-console-auditing.md

## Retrieval Guidance

- Use When: Use this chunk when identifying the available TiDB Cloud console audit log fields, their data types, and the meanings of operator, organization, project, cluster, result, and details metadata.
- Retrieval Keywords: Console audit log fields, console audit log, type, ends_at, operator_type, operator_id, operator_name, operator_ip, operator_login_method, org_id, org_name, project_id, project_name, cluster_id, cluster_name, trace_id, result, details, user, api_key, google, github, microsoft, email, success, failure
- Follow-up Guidance: The source states that trace_id is currently empty and will be available in future releases.
- Classification Note: This is reference content because it defines the audit log field schema with field names, data types, and descriptions for TiDB Cloud console audit events.

## Official Source Content

## Console audit log fields

To help you track user activities, TiDB Cloud provides the following fields for each console audit log:

| Field name | Data type | Description |
|---|---|---|
| type | string | Event type |
| ends_at | timestamp | Event time |
| operator_type | enum | Operator type: `user` or `api_key` |
| operator_id | uint64 | Operator ID |
| operator_name | string | Operator name |
| operator_ip | string | Operator's IP address |
| operator_login_method | enum | Operator's login method: `google`, `github`, `microsoft`, `email`, or `api_key` |
| org_id | uint64 | Organization ID to which the event belongs |
| org_name | string | Organization name to which the event belongs |
| project_id | uint64 | Project ID to which the event belongs |
| project_name | string | Project name to which the event belongs |
| cluster_id | uint64 | Cluster ID to which the event belongs |
| cluster_name | string | Cluster name to which the event belongs |
| trace_id | string | Trace ID of the request initiated by the operator. This field is empty currently and will be available in future releases. |
| result | enum | Event result: `success` or `failure` |
| details | json | Detailed description of the event |
