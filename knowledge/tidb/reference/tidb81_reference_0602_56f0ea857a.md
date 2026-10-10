# IMPORT INTO file source, format, and options

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-import-into.md`
- Source Title: `IMPORT INTO`
- Source Heading Path: `IMPORT INTO > Parameter description > fileLocation | IMPORT INTO > Parameter description > Format | IMPORT INTO > Parameter description > WithOptions`
- Source Line Ranges: `112-161`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `file-location`, `external-storage`, `local-files`, `csv`, `sql-format`, `parquet`, `import-options`, `detached-mode`, `checksum`, `disk-quota`, `threading`, `write-throttling`, `global-sort`, `precheck`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0602_56f0ea857a`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-import-into.md#filelocation`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ef7c34a54caafbbb0ce58f87c913f8478e11e15a0ebd45d041925cfae90082f9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-import-into#filelocation
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-import-into.md

## Retrieval Guidance

- Use When: Use this chunk when you need the exact `IMPORT INTO` file source rules, supported `CSV`/`SQL`/`PARQUET` formats, wildcard patterns in `fileLocation`, or the precise `WITH` option names and meanings.
- Retrieval Keywords: IMPORT INTO fileLocation, Amazon S3 or GCS URI path, TiDB local file path, FILE privilege, SEM enabled local file path, CSV SQL PARQUET, WITH DETACHED, CHARACTER_SET, FIELDS_TERMINATED_BY, FIELDS_ENCLOSED_BY, FIELDS_ESCAPED_BY, FIELDS_DEFINED_NULL_BY, LINES_TERMINATED_BY, SKIP_ROWS, SPLIT_FILE, DISK_QUOTA, DISABLE_TIKV_IMPORT_MODE, THREAD, MAX_WRITE_SPEED, CHECKSUM_TABLE, CLOUD_STORAGE_URI, DISABLE_PRECHECK, Global Sort, tidb_cloud_storage_uri
- Follow-up Guidance: This content also points to related identifiers and follow-up topics such as `URI Formats of External Storage Services`, `tidb_cloud_storage_uri`, the TiDB temporary directory `temp-dir`, and Global Sort permissions for S3.
- Classification Note: This is reference content because it enumerates `IMPORT INTO` parameter definitions, supported file formats, and option semantics rather than a step-by-step procedure.

## Official Source Content

### fileLocation

It specifies the storage location of the data file, which can be an Amazon S3 or GCS URI path, or a TiDB local file path.

- Amazon S3 or GCS URI path: for URI configuration details, see [URI Formats of External Storage Services](https://docs.pingcap.com/tidb/stable/external-storage-uri).

- TiDB local file path: it must be an absolute path, and the file extension must be `.csv`, `.sql`, or `.parquet`. Make sure that the files corresponding to this path are stored on the TiDB node connected by the current user, and the user has the `FILE` privilege.

> **Note:**
>
> If [SEM](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_enhanced_security) is enabled in the target cluster, the `fileLocation` cannot be specified as a local file path.

In the `fileLocation` parameter, you can specify a single file, or use the `*` and `[]` wildcards to match multiple files for import. Note that the wildcard can only be used in the file name, because it does not match directories or recursively match files in subdirectories. Taking files stored on Amazon S3 as examples, you can configure the parameter as follows:

- Import a single file: `s3://<bucket-name>/path/to/data/foo.csv`
- Import all files in a specified path: `s3://<bucket-name>/path/to/data/*`
- Import all files with the `.csv` suffix in a specified path: `s3://<bucket-name>/path/to/data/*.csv`
- Import all files with the `foo` prefix in a specified path: `s3://<bucket-name>/path/to/data/foo*`
- Import all files with the `foo` prefix and the `.csv` suffix in a specified path: `s3://<bucket-name>/path/to/data/foo*.csv`
- Import `1.csv` and `2.csv` in a specified path: `s3://<bucket-name>/path/to/data/[12].csv`
### Format

The `IMPORT INTO` statement supports three data file formats: `CSV`, `SQL`, and `PARQUET`. If not specified, the default format is `CSV`.
### WithOptions

You can use `WithOptions` to specify import options and control the data import process. For example, to execute the import of data files asynchronously in the backend, you can enable the `DETACHED` mode for the import by adding the `WITH DETACHED` option to the `IMPORT INTO` statement.

The supported options are described as follows:

| Option name | Supported data sources and formats | Description |
|:---|:---|:---|
| `CHARACTER_SET='<string>'` | CSV | Specifies the character set of the data file. The default character set is `utf8mb4`. The supported character sets include `binary`, `utf8`, `utf8mb4`, `gb18030`, `gbk`, `latin1`, and `ascii`. |
| `FIELDS_TERMINATED_BY='<string>'` | CSV | Specifies the field separator. The default separator is `,`. |
| `FIELDS_ENCLOSED_BY='<char>'` | CSV | Specifies the field delimiter. The default delimiter is `"`. |
| `FIELDS_ESCAPED_BY='<char>'` | CSV | Specifies the escape character for fields. The default escape character is `\`. |
| `FIELDS_DEFINED_NULL_BY='<string>'` | CSV | Specifies the value that represents `NULL` in the fields. The default value is `\N`. |
| `LINES_TERMINATED_BY='<string>'` | CSV | Specifies the line terminator. By default, `IMPORT INTO` automatically identifies `\n`, `\r`, or `\r\n` as line terminators. If the line terminator is one of these three, you do not need to explicitly specify this option. |
| `SKIP_ROWS=<number>` | CSV | Specifies the number of rows to skip. The default value is `0`. You can use this option to skip the header in a CSV file. If you use a wildcard to specify the source files for import, this option applies to all source files that are matched by the wildcard in `fileLocation`. |
| `SPLIT_FILE` | CSV | Splits a single CSV file into multiple smaller chunks of around 256 MiB for parallel processing to improve import efficiency. This parameter only works for **non-compressed** CSV files and has the same usage restrictions as that of TiDB Lightning [`strict-format`](https://docs.pingcap.com/tidb/stable/tidb-lightning-data-source#strict-format). Note that you need to explicitly specify `LINES_TERMINATED_BY` for this option. |
| `DISK_QUOTA='<string>'` | All file formats | Specifies the disk space threshold that can be used during data sorting. The default value is 80% of the disk space in the TiDB [temporary directory](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#temp-dir-new-in-v630). If the total disk size cannot be obtained, the default value is 50 GiB. When specifying `DISK_QUOTA` explicitly, make sure that the value does not exceed 80% of the disk space in the TiDB temporary directory. |
| `DISABLE_TIKV_IMPORT_MODE` | All file formats | Specifies whether to disable switching TiKV to import mode during the import process. By default, switching TiKV to import mode is not disabled. If there are ongoing read-write operations in the cluster, you can enable this option to avoid impact from the import process. |
| `THREAD=<number>` | All file formats and query results of `SELECT` | Specifies the concurrency for import. For `IMPORT INTO ... FROM FILE`, the default value of `THREAD` is 50% of the number of CPU cores on the TiDB node, the minimum value is `1`, and the maximum value is the number of CPU cores. For `IMPORT INTO ... FROM SELECT`, the default value of `THREAD` is `2`, the minimum value is `1`, and the maximum value is two times the number of CPU cores on the TiDB node. To import data into a new cluster without any data, it is recommended to increase this concurrency appropriately to improve import performance. If the target cluster is already used in a production environment, it is recommended to adjust this concurrency according to your application requirements. |
| `MAX_WRITE_SPEED='<string>'` | All file formats | Controls the write speed to a TiKV node. By default, there is no speed limit. For example, you can specify this option as `1MiB` to limit the write speed to 1 MiB/s. |
| `CHECKSUM_TABLE='<string>'` | All file formats | Configures whether to perform a checksum check on the target table after the import to validate the import integrity. The supported values include `"required"` (default), `"optional"`, and `"off"`. `"required"` means performing a checksum check after the import. If the checksum check fails, TiDB will return an error and the import will exit. `"optional"` means performing a checksum check after the import. If an error occurs, TiDB will return a warning and ignore the error. `"off"` means not performing a checksum check after the import. |
| `DETACHED` | All file formats | Controls whether to execute `IMPORT INTO` asynchronously. When this option is enabled, executing `IMPORT INTO` immediately returns the information of the import job (such as the `Job_ID`), and the job is executed asynchronously in the backend. |
| `CLOUD_STORAGE_URI` | All file formats | Specifies the target address where encoded KV data for [Global Sort](https://docs.pingcap.com/tidb/stable/tidb-global-sort) is stored. When `CLOUD_STORAGE_URI` is not specified, `IMPORT INTO` determines whether to use Global Sort based on the value of the system variable [`tidb_cloud_storage_uri`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_cloud_storage_uri-new-in-v740). If this system variable specifies a target storage address, `IMPORT INTO` uses this address for Global Sort. When `CLOUD_STORAGE_URI` is specified with a non-empty value, `IMPORT INTO` uses that value as the target storage address. When `CLOUD_STORAGE_URI` is specified with an empty value, local sorting is enforced. Currently, the target storage address only supports S3. For details about the URI configuration, see [Amazon S3 URI format](https://docs.pingcap.com/tidb/stable/external-storage-uri#amazon-s3-uri-format). When this feature is used, all TiDB nodes must have read and write access for the target S3 bucket, including at least these permissions: `s3:ListBucket`, `s3:GetObject`, `s3:DeleteObject`, `s3:PutObject`, `s3: AbortMultipartUpload`. |
| `DISABLE_PRECHECK` | All file formats and query results of `SELECT` | Setting this option disables pre-checks of non-critical items, such as checking whether there are CDC or PITR tasks.  |
