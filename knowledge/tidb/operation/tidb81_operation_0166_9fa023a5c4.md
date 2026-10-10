# Prepare TiDB Lightning import with checkpoints and target schema

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/migrate-large-mysql-shards-to-tidb.md`
- Source Title: `Migrate and Merge MySQL Shards of Large Datasets to TiDB`
- Source Heading Path: `Migrate and Merge MySQL Shards of Large Datasets to TiDB > Step 2. Start TiDB Lightning to import full exported data | Migrate and Merge MySQL Shards of Large Datasets to TiDB > Step 2. Start TiDB Lightning to import full exported data > Checkpoints | Migrate and Merge MySQL Shards of Large Datasets to TiDB > Step 2. Start TiDB Lightning to import full exported data > Create a target schema`
- Source Line Ranges: `117-151`
- Source Scope: `self_managed`
- Primary Component: `lightning`
- Related Components: `tidb`, `shared`
- Topic Tags: `full-import`, `checkpoints`, `restart`, `error-handling`, `target-schema`, `table-creation`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0166_9fa023a5c4`
- Source ID: `tidb-docs-8.1:migrate-large-mysql-shards-to-tidb.md#step-2-start-tidb-lightning-to-import-full-exported-data`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c86306d345fa28e101bc23a8c3611b111ff0011e218eab78492ef084ca7ac7f7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/migrate-large-mysql-shards-to-tidb#step-2-start-tidb-lightning-to-import-full-exported-data
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/migrate-large-mysql-shards-to-tidb.md

## Retrieval Guidance

- Use When: Use this chunk when you need TiDB Lightning checkpoint behavior for long-running imports and the target table schema to create before importing merged shard data.
- Retrieval Keywords: Step 2. Start TiDB Lightning to import full exported data, checkpoints, TiDB Lightning Checkpoints, interrupted import task can be resumed, tidb-lightning-ctl, --checkpoint-error-destroy, --checkpoint-error-ignore, --checkpoint-remove, unrecoverable errors, data corruption, Create a target schema, CREATE TABLE `table5`, mydb.table5, INDEX (`id`), UNIQUE KEY `sid` (`sid`)
- Follow-up Guidance: The source says that if TiDB Lightning crashes due to unrecoverable errors, you must resolve the errors by using the `tidb-lightning-ctl` command before proceeding with other steps.
- Classification Note: This is classified as operation because the content focuses on import task handling, restart and error processing with checkpoints, and preparing the downstream target schema.

## Official Source Content

## Step 2. Start TiDB Lightning to import full exported data

Before starting TiDB Lightning for migration, it is recommended that you understand how to handle checkpoints, and then choose the appropriate way to proceed according to your needs.
### Checkpoints

Migrating a large volume of data usually takes hours or even days. There is a certain chance that the long-running process is interrupted unexpectedly. It can be very frustrating to redo everything from scratch, even if some part of data has already been imported.

Fortunately, TiDB Lightning provides a feature called `checkpoints`, which makes TiDB Lightning save the import progress as `checkpoints` from time to time, so that an interrupted import task can be resumed from the latest checkpoint upon restart.

If the TiDB Lightning task crashes due to unrecoverable errors (for example, data corruption), it will not pick up from the checkpoint, but will report an error and quit the task. To ensure the safety of the imported data, you must resolve these errors by using the `tidb-lightning-ctl` command before proceeding with other steps. The options include:

* --checkpoint-error-destroy: This option allows you to restart importing data into failed target tables from scratch by destroying all the existing data in those tables first.
* --checkpoint-error-ignore: If migration has failed, this option clears the error status as if no errors ever happened.
* --checkpoint-remove: This option simply clears all checkpoints, regardless of errors.

For more information, see [TiDB Lightning Checkpoints](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-checkpoints).
### Create a target schema

Create `mydb.table5` at downstream.

```sql
CREATE TABLE `table5` (
  `id` bigint(20) NOT NULL,
  `sid` bigint(20) NOT NULL,
  `pid` bigint(20) NOT NULL,
  `comment` varchar(255) DEFAULT NULL,
  INDEX (`id`),
  UNIQUE KEY `sid` (`sid`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1
```
