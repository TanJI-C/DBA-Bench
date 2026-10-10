# TiDB Cloud SQL statement and function limitations

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/limited-sql-features.md`
- Source Title: `Limited SQL Features on TiDB Cloud`
- Source Heading Path: `Limited SQL features on TiDB Cloud | Limited SQL features on TiDB Cloud > Statements | Limited SQL features on TiDB Cloud > Statements > Placement and range management | Limited SQL features on TiDB Cloud > Statements > Resource groups | Limited SQL features on TiDB Cloud > Statements > Others | Limited SQL features on TiDB Cloud > Functions and operators`
- Source Line Ranges: `5-70`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `sql`, `tidb`
- Topic Tags: `sql-statements`, `functions`, `placement-policies`, `resource-groups`, `backup-restore`, `telemetry`, `load-data`, `plugins`, `tls`, `plan-replayer`, `serverless`, `dedicated`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0811_4b1d5f4b59`
- Source ID: `tidb-docs-8.1:tidb-cloud/limited-sql-features.md#limited-sql-features-on-tidb-cloud`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `bb671571539c48527ae891cd46b9eea669f959e9bcb2951ed4acbb1abab53a29`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/limited-sql-features#limited-sql-features-on-tidb-cloud
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/limited-sql-features.md

## Retrieval Guidance

- Use When: Use this chunk when checking whether a specific SQL statement, operator, or function is supported in TiDB Cloud Dedicated versus TiDB Cloud Serverless, especially for placement policies, resource groups, backup and restore, telemetry, plugins, TLS reload, LOAD DATA, PLAN REPLAYER, or SLEEP().
- Retrieval Keywords: TiDB Cloud limited SQL features, TiDB Cloud SQL statement limitations, TiDB Cloud Dedicated Serverless support matrix, ALTER PLACEMENT POLICY, CREATE PLACEMENT POLICY, SHOW PLACEMENT, SHOW TABLE REGIONS, SPLIT REGION, ALTER RESOURCE GROUP, CREATE RESOURCE GROUP, SET RESOURCE GROUP, BACKUP, RESTORE, SHOW BACKUPS, SHOW RESTORES, ADMIN RESET TELEMETRY_ID, ADMIN SHOW TELEMETRY, ADMIN SHOW SLOW, ADMIN PLUGINS ENABLE, ADMIN PLUGINS DISABLE, ALTER INSTANCE RELOAD TLS, LOAD DATA LOCAL INFILE, LOAD DATA INFILE Amazon S3, LOAD DATA INFILE Google Cloud Storage, CHANGE DRAINER, CHANGE PUMP, FLASHBACK CLUSTER, LOAD STATS, SELECT ... INTO OUTFILE, SET CONFIG, SHOW CONFIG, SHOW PLUGINS, SHOW DRAINER STATUS, SHOW PUMP STATUS, SHUTDOWN, PLAN REPLAYER, SLEEP() function 300 seconds
- Follow-up Guidance: If the needed SQL feature is in the gap between TiDB Self-Managed and TiDB Cloud Dedicated/Serverless, the document says to contact TiDB Cloud support for a feature request.
- Classification Note: This is a reference chunk because it presents support and limitation tables for SQL statements, functions, and operators on TiDB Cloud Dedicated and Serverless.

## Official Source Content

# Limited SQL features on TiDB Cloud

TiDB Cloud works with almost all workloads that TiDB supports, but there are some feature differences between TiDB Self-Managed and TiDB Cloud Dedicated/Serverless. This document describes the limitations of SQL features on TiDB Cloud. We are constantly filling in the feature gaps between TiDB Self-Managed and TiDB Cloud Dedicated/Serverless. If you require these features or capabilities in the gap, [contact us](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support) for a feature request.
## Statements
### Placement and range management

| Statement | TiDB Cloud Dedicated | TiDB Cloud Serverless |
|:-|:-|:-|
| `ALTER PLACEMENT POLICY` | Supported | Not supported [^1] |
| `CREATE PLACEMENT POLICY` | Supported | Not supported [^1] |
| `DROP PLACEMENT POLICY` | Supported | Not supported [^1] |
| `SHOW CREATE PLACEMENT POLICY` | Supported | Not supported [^1] |
| `SHOW PLACEMENT` | Supported | Not supported [^1] |
| `SHOW PLACEMENT FOR` | Supported | Not supported [^1] |
| `SHOW PLACEMENT LABELS` | Supported | Not supported [^1] |
| `SHOW TABLE REGIONS` | Supported | Not supported [^1] |
| `SPLIT REGION` | Supported | Not supported [^1] |
### Resource groups

| Statement | TiDB Cloud Dedicated | TiDB Cloud Serverless |
|:-|:-|:-|
| `ALTER RESOURCE GROUP` | Supported | Not supported [^2] |
| `CALIBRATE RESOURCE` | Not supported | Not supported [^2] |
| `CREATE RESOURCE GROUP` | Supported | Not supported [^2] |
| `DROP RESOURCE GROUP` | Supported | Not supported [^2] |
| `SET RESOURCE GROUP` | Supported | Not supported [^2] |
| `SHOW CREATE RESOURCE GROUP` | Supported | Not supported [^2] |
### Others

| Statement | TiDB Cloud Dedicated | TiDB Cloud Serverless |
|:-|:-|:-|
| `BACKUP` | Supported | Not supported [^3] |
| `SHOW BACKUPS` | Supported | Not supported [^3] |
| `RESTORE` | Supported | Not supported [^3] |
| `SHOW RESTORES` | Supported | Not supported [^3] |
| `ADMIN RESET TELEMETRY_ID` | Supported | Telemetry is not supported on TiDB Cloud Serverless. |
| `ADMIN SHOW TELEMETRY` | Not supported [^4] | Not supported [^4] |
| `ADMIN SHOW SLOW` | Supported | Not supported [^5] |
| `ADMIN PLUGINS ENABLE` | Supported | Not supported [^8] |
| `ADMIN PLUGINS DISABLE` | Supported | Not supported [^8] |
| `ALTER INSTANCE RELOAD TLS` | Supported | TiDB Cloud Serverless automatically refreshes the TLS certificate. |
| `LOAD DATA INFILE` | Supports `LOAD DATA LOCAL INFILE`, and `LOAD DATA INFILE` from Amazon S3 or Google Cloud Storage | Only supports `LOAD DATA LOCAL INFILE` |
| `CHANGE DRAINER` | Not supported [^7] | Not supported [^7] |
| `CHANGE PUMP` | Not supported [^7] | Not supported [^7] |
| `FLASHBACK CLUSTER` | Supported | Not supported [^3] |
| `LOAD STATS` | Supported | Not supported |
| `SELECT ... INTO OUTFILE` | Not supported [^4] | Not supported [^4] |
| `SET CONFIG` | Not supported [^4] | Not supported [^4] |
| `SHOW CONFIG` | Not supported [^4] | Not supported [^4] |
| `SHOW DRAINER STATUS` | Not supported [^7] | Not supported [^7] |
| `SHOW PLUGINS` | Supported | Not supported [^8] |
| `SHOW PUMP STATUS` | Not supported [^7] | Not supported [^7] |
| `SHUTDOWN` | Not supported [^4] | Not supported [^4] |
| `PLAN REPLAYER` | Supported | Supported in a different way[^11] |
## Functions and operators

| Function and operator | TiDB Cloud Dedicated | TiDB Cloud Serverless |
|:-|:-|:-|
| `SLEEP` | No Limitation | The [`SLEEP()` function](https://docs.pingcap.com/tidbcloud/miscellaneous-functions) has a limitation wherein it can only support a maximum sleep time of 300 seconds.|
