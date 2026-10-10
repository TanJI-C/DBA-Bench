# Lightning data source naming patterns and renaming methods

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-lightning/tidb-lightning-data-source.md`
- Source Title: `TiDB Lightning Data Sources`
- Source Heading Path: `TiDB Lightning Data Sources | TiDB Lightning Data Sources > Rename databases and tables | TiDB Lightning Data Sources > Rename databases and tables > Rename files in batch | TiDB Lightning Data Sources > Rename databases and tables > Use regular expressions to replace names online`
- Source Line Ranges: `5-99`
- Source Scope: `self_managed`
- Primary Component: `lightning`
- Related Components: `shared`, `tidb`
- Topic Tags: `data-source-dir`, `file-patterns`, `schema-files`, `compressed-files`, `parallel-import`, `file-renaming`, `regex-matching`, `mydumper-files`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0335_0cf66ff8fa`
- Source ID: `tidb-docs-8.1:tidb-lightning/tidb-lightning-data-source.md#tidb-lightning-data-sources`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `951d9bd5c20ab924de80bcdf2317524b67eb840a7a2543578389c78086e91ca8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-data-source#tidb-lightning-data-sources
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-lightning/tidb-lightning-data-source.md

## Retrieval Guidance

- Use When: Use this when you need the TiDB Lightning `data-source-dir` filename patterns, compressed file naming rules, or the documented ways to rename imported databases and tables by batch renaming files or matching `[[mydumper.files]]` patterns.
- Retrieval Keywords: data-source-dir, ${db_name}.${table_name}-schema.sql, ${db_name}-schema-create.sql, ${db_name}.${table_name}.${csv|sql|parquet}, ${db_name}.${table_name}.001.${csv|sql|parquet}, ${db_name}.${table_name}.${csv|sql|parquet}.{compress}, region-concurrency, rename srcdb. tgtdb. *.sql, [[mydumper.files]], pattern, schema-schema, table-schema, compression = '$4', official Snappy format, gzip, regular expressions to replace names online
- Follow-up Guidance: The content also states that after modifying the database name it is recommended to delete the `${db_name}-schema-create.sql` file from `data-source-dir`, and if the table name changes you also need to modify the table name in the `${db_name}.${table_name}-schema.sql` file.
- Classification Note: This chunk is classified as configuration for TiDB Lightning because it defines `data-source-dir`, filename matching patterns, and `[[mydumper.files]]` regex mapping fields such as `pattern`, `schema`, `table`, `type`, and `compression`.

## Official Source Content

# TiDB Lightning Data Sources

TiDB Lightning supports importing data from multiple data sources to TiDB clusters, including CSV, SQL, and Parquet files.

To specify the data source for TiDB Lightning, use the following configuration:

```toml
[mydumper]
# Local source data directory or the URI of the external storage such as S3. For more information about the URI of the external storage, see https://docs.pingcap.com/tidb/v8.1/backup-and-restore-storages#uri-format.
data-source-dir = "/data/my_database"
```

When TiDB Lightning is running, it looks for all files that match the pattern of `data-source-dir`.

| File | Type | Pattern |
| --------- | -------- | ------- |
| Schema file | Contains the `CREATE TABLE` DDL statement | `${db_name}.${table_name}-schema.sql` |
| Schema file | Contains the `CREATE DATABASE` DDL statement| `${db_name}-schema-create.sql` |
| Data file | If the data file contains data for a whole table, the file is imported into a table named `${db_name}.${table_name}` | <code>\${db_name}.\${table_name}.\${csv\|sql\|parquet}</code> |
| Data file | If the data for a table is split into multiple data files, each data file must be suffixed with a number in its filename | <code>\${db_name}.\${table_name}.001.\${csv\|sql\|parquet}</code> |
| Compressed file | If the file contains a compression suffix, such as `gzip`, `snappy`, or `zstd`, TiDB Lightning will decompress the file before importing it. Note that the Snappy compressed file must be in the [official Snappy format](https://github.com/google/snappy). Other variants of Snappy compression are not supported. | <code>\${db_name}.\${table_name}.\${csv\|sql\|parquet}.{compress}</code> |

TiDB Lightning processes data in parallel as much as possible. Because files must be read in sequence, the data processing concurrency is at the file level (controlled by `region-concurrency`). Therefore, when the imported file is large, the import performance is poor. It is recommended to limit the size of the imported file to no greater than 256 MiB to achieve the best performance.
## Rename databases and tables

TiDB Lightning follows filename patterns to import data to the corresponding database and table. If the database or table names change, you can either rename the files and then import them, or use regular expressions to replace the names online.
### Rename files in batch

If you are using Red Hat Linux or a distribution based on Red Hat Linux, you can use the `rename` command to batch rename files in the `data-source-dir` directory. 

For example:

```shell
rename srcdb. tgtdb. *.sql
```

After you modify the database name, it is recommended that you delete the `${db_name}-schema-create.sql` file that contains the `CREATE DATABASE` DDL statement from the `data-source-dir` directory. If you want to modify the table name as well, you also need to modify the table name in the `${db_name}.${table_name}-schema.sql` file that contains the `CREATE TABLE` DDL statement.
### Use regular expressions to replace names online

To use regular expressions to replace names online, you can use the `pattern` configuration within `[[mydumper.files]]` to match filenames, and replace `schema` and `table` with your desired names. For more information, see [Match customized files](#match-customized-files).

The following is an example of using regular expressions to replace names online. In this example:

- The match rule for the data file `pattern` is `^({schema_regrex})\.({table_regrex})\.({file_serial_regrex})\.(csv|parquet|sql)`.
- Specify `schema` as `'$1'`, which means that the value of the first regular expression `schema_regrex` remains unchanged. Or specify `schema` as a string, such as `'tgtdb'`, which means a fixed target database name.
- Specify `table` as `'$2'`, which means that the value of the second regular expression `table_regrex` remains unchanged. Or specify `table` as a string, such as `'t1'`, which means a fixed target table name.
- Specify `type` as `'$3'`, which means the data file type. You can specify `type` as either `"table-schema"` (representing the `schema.sql` file) or `"schema-schema"` (representing the `schema-create.sql` file).

```toml
[mydumper]
data-source-dir = "/some-subdir/some-database/"
[[mydumper.files]]
pattern = '^(srcdb)\.(.*?)-schema-create\.sql'
schema = 'tgtdb'
type = "schema-schema"
[[mydumper.files]]
pattern = '^(srcdb)\.(.*?)-schema\.sql'
schema = 'tgtdb'
table = '$2'
type = "table-schema"
[[mydumper.files]]
pattern = '^(srcdb)\.(.*?)\.(?:[0-9]+)\.(csv|parquet|sql)'
schema = 'tgtdb'
table = '$2'
type = '$3'
```

If you are using `gzip` to back up data files, you need to configure the compression format accordingly. The matching rule of the data file `pattern` is `'^({schema_regrex})\.({table_regrex})\.({file_serial_regrex})\.(csv|parquet|sql)\.(gz)'`. You can specify `compression` as `'$4'` to represent the compressed file format. For example:

```toml
[mydumper]
data-source-dir = "/some-subdir/some-database/"
[[mydumper.files]]
pattern = '^(srcdb)\.(.*?)-schema-create\.(sql)\.(gz)'
schema = 'tgtdb'
type = "schema-schema"
compression = '$4'
[[mydumper.files]]
pattern = '^(srcdb)\.(.*?)-schema\.(sql)\.(gz)'
schema = 'tgtdb'
table = '$2'
type = "table-schema"
compression = '$4'
[[mydumper.files]]
pattern = '^(srcdb)\.(.*?)\.(?:[0-9]+)\.(sql)\.(gz)'
schema = 'tgtdb'
table = '$2'
type = '$3'
compression = '$4'
```
