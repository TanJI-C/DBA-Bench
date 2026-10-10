# Optimistic mode implementation principle and schema merge examples

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/feature-shard-merge-optimistic.md`
- Source Title: `Merge and Migrate Data from Sharded Tables in Optimistic Mode`
- Source Heading Path: `Merge and Migrate Data from Sharded Tables in Optimistic Mode > Implementation principle | Merge and Migrate Data from Sharded Tables in Optimistic Mode > Implementation principle > Examples`
- Source Line Ranges: `106-193`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tidb`
- Topic Tags: `implementation principle`, `dm-worker`, `dm-master`, `schema merge`, `composite schema`, `ddl migration`, `dml migration`, `sharded tables`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0026_10190bb86d`
- Source ID: `tidb-docs-8.1:dm/feature-shard-merge-optimistic.md#implementation-principle`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8e0a108026d1defd6e6f248814df7a609be2da47697b5b88f3091728294a029a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/feature-shard-merge-optimistic#implementation-principle
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/feature-shard-merge-optimistic.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks how optimistic sharding works internally in DM, including the roles of DM-worker and DM-master, composite schema merging, and why some upstream DDL does not immediately become downstream DDL.
- Retrieval Keywords: implementation principle, DM-worker, DM-master, composite schema, merge these schemas, compatible with DML statements, DML statements are directly migrated, tbl00 tbl01 tbl02, ALTER TABLE `tbl00` ADD COLUMN `Level` INT;, ALTER TABLE `tbl01` DROP COLUMN `Name`;, ALTER TABLE `tbl` DROP COLUMN `Name`;, sharded tables to downstream tbl
- Follow-up Guidance: The examples trace adding `Level` and dropping `Name` across `tbl00`, `tbl01`, and `tbl02`, showing when DM-master performs no operation and when the downstream `tbl` can safely execute `ALTER TABLE `tbl` DROP COLUMN `Name`;`.
- Classification Note: This is classified as architecture because the content explains the internal optimistic mode flow between DM-worker and DM-master and the schema-merge logic used for downstream DDL and DML migration.

## Official Source Content

## Implementation principle

In the optimistic mode, after DM-worker receives the DDL statement from the upstream, it forwards the updated table schema to DM-master. DM-worker tracks the current schema of each sharded table, and DM-master merges these schemas into a composite schema that is compatible with DML statements of every sharded table. Then DM-master migrates the corresponding DDL statement to the downstream. DML statements are directly migrated to the downstream.

![optimistic-ddl-flow](/media/dm/optimistic-ddl-flow.png)
### Examples

Assume the upstream MySQL has three sharded tables (`tbl00`, `tbl01`, and `tbl02`). Merge and migrate these sharded tables to the `tbl` table in the downstream TiDB. See the following image:

![optimistic-ddl-example-1](/media/dm/optimistic-ddl-example-1.png)

Add a `Level` column in the upstream:

```sql
ALTER TABLE `tbl00` ADD COLUMN `Level` INT;
```

![optimistic-ddl-example-2](/media/dm/optimistic-ddl-example-2.png)

Then TiDB will receive the DML statement from `tbl00` (with the `Level` column) and the DML statement from the `tbl01` and `tbl02` tables (without the `Level` column).

![optimistic-ddl-example-3](/media/dm/optimistic-ddl-example-3.png)

The following DML statements can be migrated to the downstream without any modification:

```sql
UPDATE `tbl00` SET `Level` = 9 WHERE `ID` = 1;
INSERT INTO `tbl02` (`ID`, `Name`) VALUES (27, 'Tony');
```

![optimistic-ddl-example-4](/media/dm/optimistic-ddl-example-4.png)

Also add a `Level` column in `tbl01`:

```sql
ALTER TABLE `tbl01` ADD COLUMN `Level` INT;
```

![optimistic-ddl-example-5](/media/dm/optimistic-ddl-example-5.png)

At this time, the downstream already have had the same `Level` column, so DM-master performs no operation after comparing the table schemas.

Drop a `Name` column in `tbl01`:

```sql
ALTER TABLE `tbl01` DROP COLUMN `Name`;
```

![optimistic-ddl-example-6](/media/dm/optimistic-ddl-example-6.png)

Then the downstream will receive the DML statements from `tbl00` and `tbl02` with the `Name` column, so this column is not immediately dropped.

In the same way, all DML statements can still be migrated to the downstream:

```sql
INSERT INTO `tbl01` (`ID`, `Level`) VALUES (15, 7);
UPDATE `tbl00` SET `Level` = 5 WHERE `ID` = 5;
```

![optimistic-ddl-example-7](/media/dm/optimistic-ddl-example-7.png)

Add a `Level` column in `tbl02`:

```sql
ALTER TABLE `tbl02` ADD COLUMN `Level` INT;
```

![optimistic-ddl-example-8](/media/dm/optimistic-ddl-example-8.png)

By then, all sharded tables have the `Level` column.

Drop the `Name` columns in `tbl00` and `tbl02` respectively:

```sql
ALTER TABLE `tbl00` DROP COLUMN `Name`;
ALTER TABLE `tbl02` DROP COLUMN `Name`;
```

![optimistic-ddl-example-9](/media/dm/optimistic-ddl-example-9.png)

By then, the `Name` columns are dropped from all sharded tables and can be safely dropped in the downstream:

```sql
ALTER TABLE `tbl` DROP COLUMN `Name`;
```

![optimistic-ddl-example-10](/media/dm/optimistic-ddl-example-10.png)
