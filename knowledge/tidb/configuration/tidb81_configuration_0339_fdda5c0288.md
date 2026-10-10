# Configure parallel import for single-table files

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-lightning/tidb-lightning-distributed-import.md`
- Source Title: `Use TiDB Lightning to Import Data in Parallel`
- Source Heading Path: `Use TiDB Lightning to Import Data in Parallel > Example 2: Import single tables in parallel`
- Source Line Ranges: `144-184`
- Source Scope: `self_managed`
- Primary Component: `lightning`
- Related Components: `br`, `dumpling`, `shared`
- Topic Tags: `single-table-import`, `amazon-s3`, `external-storage`, `file-patterns`, `parallel-import`, `mydumper-files`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0339_fdda5c0288`
- Source ID: `tidb-docs-8.1:tidb-lightning/tidb-lightning-distributed-import.md#example-2-import-single-tables-in-parallel`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `fc98a04bcda1b3030dd6efe0c15e79d124c9a8b8e61f284492f3edfe5f7e460d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-distributed-import#example-2-import-single-tables-in-parallel
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-lightning/tidb-lightning-distributed-import.md

## Retrieval Guidance

- Use When: Use this chunk when you need the configuration pattern for parallel import of a single table split across many files, especially from Amazon S3.
- Retrieval Keywords: Import single tables in parallel, Amazon S3, URI Formats of External Storage Services, [[mydumper.files]], pattern = '(?i)^(?:[^/]*/)*my_db-schema-create\\.sql', pattern = '(?i)^(?:[^/]*/)*my_db\\.my_table-schema\\.sql', pattern = '(?i)^(?:[^/]*/)*my_db\\.my_table\\.(0[0-4][0-9][0-9][0-9]|05000)\\.sql', parallel-import = true, my_db.my_table.00001.sql, my_db.my_table.10000.sql, --filesize, --where
- Follow-up Guidance: The other TiDB Lightning instance can be configured to import only the `05001 ~ 10000` data files, and the remaining steps follow Example 1.
- Classification Note: This is classified as a configuration chunk because it provides concrete `mydumper.files` patterns and the `tikv-importer.parallel-import = true` setting for parallel single-table import.

## Official Source Content

## Example 2: Import single tables in parallel

TiDB Lightning also supports parallel import of single tables. For example, import multiple single tables stored in Amazon S3 by different TiDB Lightning instances into the downstream TiDB cluster in parallel. This method can speed up the overall import speed. When remote storages such as Amazon S3 is used, the configuration parameters of TiDB Lightning are the same as those of BR. For more details, see [URI Formats of External Storage Services](https://docs.pingcap.com/tidb/stable/external-storage-uri).

> **Note:**
>
>In the local environment, you can use the `--filesize` or `--where` parameter of Dumpling to divide the data of a single table into different parts and export it to the local disks of multiple servers in advance. This way, you can still perform parallel import. The configuration is the same as Example 1.

Assuming that the source files are stored in Amazon S3, the table files are `my_db.my_table.00001.sql` ~ `my_db.my_table.10000.sql`, a total of 10,000 SQL files. If you want to use 2 TiDB Lightning instances to speed up the import, you need to add the following settings in the configuration file:

```
[[mydumper.files]]
# the db schema file
pattern = '(?i)^(?:[^/]*/)*my_db-schema-create\.sql'
schema = "my_db"
type = "schema-schema"

[[mydumper.files]]
# the table schema file
pattern = '(?i)^(?:[^/]*/)*my_db\.my_table-schema\.sql'
schema = "my_db"
table = "my_table"
type = "table-schema"

[[mydumper.files]]
# Only import 00001~05000 and ignore other files
pattern = '(?i)^(?:[^/]*/)*my_db\.my_table\.(0[0-4][0-9][0-9][0-9]|05000)\.sql'
schema = "my_db"
table = "my_table"
type = "sql"

[tikv-importer]
# Whether to allow importing data into tables that already have data. The default value is `false`.
# When using parallel import, because multiple TiDB Lightning instances import a table at the same time, this configuration item must be set to `true`.
parallel-import = true
```

You can modify the configuration of the other instance to only import the `05001 ~ 10000` data files.

For other steps, see the relevant steps in Example 1.
