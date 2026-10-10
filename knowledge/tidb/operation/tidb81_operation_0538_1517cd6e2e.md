# Reload privilege changes with FLUSH PRIVILEGES

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/user-account-management.md`
- Source Title: `TiDB User Account Management`
- Source Heading Path: `TiDB User Account Management > `FLUSH PRIVILEGES``
- Source Line Ranges: `227-237`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `sql`
- Topic Tags: `flush-privileges`, `privilege-cache`, `user-privileges`, `direct-table-modification`, `cache-reload`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0538_1517cd6e2e`
- Source ID: `tidb-docs-8.1:user-account-management.md#flush-privileges`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `50498bcc153afa41a855bbd853fa43edf91f174c8b8eed86a07798cf52f65802`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/user-account-management#flush-privileges
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/user-account-management.md

## Retrieval Guidance

- Use When: Use this chunk when looking for when `FLUSH PRIVILEGES` is needed to reload privilege changes and how TiDB privilege cache behavior affects propagation.
- Retrieval Keywords: FLUSH PRIVILEGES, privilege tables, TiKV server, TiDB caches this information inside the process, CREATE USER, GRANT, periodically reload the cache information, about 15 minutes, temporarily unavailable network, Privilege Management
- Follow-up Guidance: It explains that changes from `CREATE USER`, `GRANT`, and similar statements usually take effect quickly cluster-wide, but may take about 15 minutes if cache reload is delayed by factors such as temporarily unavailable network.
- Classification Note: This is classified as operation because it covers applying privilege changes and understanding cache reload behavior during normal privilege management.

## Official Source Content

## `FLUSH PRIVILEGES`

Information related to users and privileges is stored in the TiKV server, and TiDB caches this information inside the process. Generally, modification of the related information through `CREATE USER`, `GRANT`, and other statements takes effect quickly within the entire cluster. If the operation is affected by some factors such as temporarily unavailable network, the modification will take effect in about 15 minutes because TiDB will periodically reload the cache information.

If you modified the privilege tables directly, run the following command to apply changes immediately:

```sql
FLUSH PRIVILEGES;
```

For details, see [Privilege Management](https://docs.pingcap.com/tidb/stable/privilege-management).
