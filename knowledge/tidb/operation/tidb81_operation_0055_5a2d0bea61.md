# Non-transactional bulk-delete prerequisites, syntax, and example

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-delete-data.md`
- Source Title: `Delete Data`
- Source Heading Path: `Delete Data > Non-transactional bulk-delete | Delete Data > Non-transactional bulk-delete > Prerequisites of non-transactional bulk-delete | Delete Data > Non-transactional bulk-delete > SQL syntax for non-transactional bulk-delete | Delete Data > Non-transactional bulk-delete > Example of non-transactional bulk-delete | Delete Data > Need help?`
- Source Line Ranges: `379-427`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `non-transactional-dml`, `bulk-delete`, `prerequisites`, `syntax`, `batch-processing`, `data-loss-warning`, `version-specific`, `support`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0055_5a2d0bea61`
- Source ID: `tidb-docs-8.1:develop/dev-guide-delete-data.md#non-transactional-bulk-delete`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e6db585b5613f97b1a0bc446808261001113de4a18e20841cc456d995309b6e8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-delete-data#non-transactional-bulk-delete
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-delete-data.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the prerequisites, syntax, cautions, version note, and example SQL for non-transactional bulk-delete with `BATCH ON ... LIMIT` in TiDB.
- Retrieval Keywords: Non-transactional bulk-delete, non-transactional DML statements, Since v6.1.0, BATCH ON {shard_column} LIMIT {batch_size} {delete_statement};, BATCH ON `rated_at` LIMIT 1000 DELETE FROM `ratings`, compromises transactional atomicity and isolation, data loss, prerequisites of non-transactional bulk-delete
- Follow-up Guidance: For detailed information, see the Non-transactional DML Statements documentation; the page also lists Discord, Slack, and support ticket links under Need help.
- Classification Note: This is classified as an operation chunk because it describes how to perform non-transactional bulk-delete, including prerequisites, SQL syntax, and an example statement.

## Official Source Content

## Non-transactional bulk-delete

> **Note:**
>
> Since v6.1.0, TiDB supports the [non-transactional DML statements](https://docs.pingcap.com/tidb/stable/non-transactional-dml). This feature is not available for versions earlier than TiDB v6.1.0.
### Prerequisites of non-transactional bulk-delete

Before using the non-transactional bulk-delete, make sure you have read the [Non-Transactional DML statements documentation](https://docs.pingcap.com/tidb/stable/non-transactional-dml) first. The non-transactional bulk-delete improves the performance and ease of use in batch data processing scenarios but compromises transactional atomicity and isolation.

Therefore, you should use it carefully to avoid serious consequences (such as data loss) due to mishandling.
### SQL syntax for non-transactional bulk-delete

The SQL syntax for non-transactional bulk-delete statement is as follows:

```sql
BATCH ON {shard_column} LIMIT {batch_size} {delete_statement};
```

| Parameter Name | Description |
| :--------: | :------------: |
| `{shard_column}` | The column used to divide batches.      |
| `{batch_size}`   | Control the size of each batch. |
| `{delete_statement}` | The `DELETE` statement. |

The preceding example only shows a simple use case of a non-transactional bulk-delete statement. For detailed information, see [Non-transactional DML Statements](https://docs.pingcap.com/tidb/stable/non-transactional-dml).
### Example of non-transactional bulk-delete

In the same scenario as the [Bulk-delete example](#bulk-delete-example), the following SQL statement shows how to perform a non-transactional bulk-delete:

```sql
BATCH ON `rated_at` LIMIT 1000 DELETE FROM `ratings` WHERE `rated_at` >= "2022-04-15 00:00:00" AND  `rated_at` <= "2022-04-15 00:15:00";
```
## Need help?

Ask the community on [Discord](https://discord.gg/DQZ2dy3cuc?utm_source=doc) or [Slack](https://slack.tidb.io/invite?team=tidb-community&channel=everyone&ref=pingcap-docs), or [submit a support ticket](https://docs.pingcap.com/tidb/stable/support).

Ask the community on [Discord](https://discord.gg/DQZ2dy3cuc?utm_source=doc) or [Slack](https://slack.tidb.io/invite?team=tidb-community&channel=everyone&ref=pingcap-docs), or [submit a support ticket](https://tidb.support.pingcap.com/).
