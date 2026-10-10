# Optimistic mode risks and inconsistency scenarios

## Knowledge Metadata

- Knowledge Type: `recovery`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/feature-shard-merge-optimistic.md`
- Source Title: `Merge and Migrate Data from Sharded Tables in Optimistic Mode`
- Source Heading Path: `Merge and Migrate Data from Sharded Tables in Optimistic Mode > Risks | Merge and Migrate Data from Sharded Tables in Optimistic Mode > Risks > Operations that cause data inconsistency | Merge and Migrate Data from Sharded Tables in Optimistic Mode > Risks > Example`
- Source Line Ranges: `66-105`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tidb`
- Topic Tags: `risks`, `data inconsistency`, `schema incompatibility`, `rollback`, `default values`, `manual fix`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_recovery_0018_97faa75bf5`
- Source ID: `tidb-docs-8.1:dm/feature-shard-merge-optimistic.md#risks`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `567529e5e61b14ce17cf1936a7224a19cfed92bebb75bd828af66efd51b299e0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/feature-shard-merge-optimistic#risks
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/feature-shard-merge-optimistic.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks about optimistic mode risk scenarios, examples of schema incompatibility, rollback-related inconsistency, or a case where DM reports an error but data inconsistency must be fixed manually.
- Retrieval Keywords: optimistic mode risks, data inconsistency, schema incompatible, different default values, generated columns different expressions, indexes same name different keys, drop a column X and then add this column back, ALTER TABLE `tbl01` ADD COLUMN `Age` INT DEFAULT 0;, ALTER TABLE `tbl00` ADD COLUMN `Age` INT DEFAULT -1;, manual fix data inconsistency, DM will report the error
- Follow-up Guidance: The example shows `Age` added with `DEFAULT 0` in `tbl01` and `DEFAULT -1` in `tbl00`, which DM reports as incompatible and requiring manual fixing of the inconsistency.
- Classification Note: This is classified as recovery because the content focuses on failure and inconsistency situations in optimistic mode, including reported errors and cases that require manual fixing.

## Official Source Content

## Risks

When you use the optimistic mode for a migration task, a DDL statement is migrated to the downstream immediately. If this mode is misused, data inconsistency between the upstream and the downstream might occur.
### Operations that cause data inconsistency

- The schema of each sharded table is incompatible with each other. For example:
    - Two columns of the same name are added to two sharded tables respectively, but the columns are of different types.
    - Two columns of the same name are added to two sharded tables respectively, but the columns have different default values.
    - Two generated columns of the same name are added to two sharded tables respectively, but the columns are generated using different expressions.
    - Two indexes of the same name are added to two sharded tables respectively, but the keys are different.
    - Other different table schemas with the same name.
- Execute the DDL statement that can corrupt data in the sharded table and then try to roll back.

    For example, drop a column `X` and then add this column back.
### Example

Merge and migrate the following three sharded tables to TiDB:

![optimistic-ddl-fail-example-1](/media/dm/optimistic-ddl-fail-example-1.png)

Add a new column `Age` in `tbl01` and set the default value of the column to `0`:

```sql
ALTER TABLE `tbl01` ADD COLUMN `Age` INT DEFAULT 0;
```

![optimistic-ddl-fail-example-2](/media/dm/optimistic-ddl-fail-example-2.png)

Add a new column `Age` in `tbl00` and set the default value of the column to `-1`:

```sql
ALTER TABLE `tbl00` ADD COLUMN `Age` INT DEFAULT -1;
```

![optimistic-ddl-fail-example-3](/media/dm/optimistic-ddl-fail-example-3.png)

By then, the `Age` column of `tbl00` is inconsistent because `DEFAULT 0` and `DEFAULT -1` are incompatible with each other. In this situation, DM will report the error, but you have to manually fix the data inconsistency.
