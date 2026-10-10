# TiDB Lightning CSV import configuration and strict-format tuning

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/migrate-from-csv-files-to-tidb.md`
- Source Title: `Migrate Data from CSV Files to TiDB`
- Source Heading Path: `Migrate Data from CSV Files to TiDB > Step 3. Create the configuration file | Migrate Data from CSV Files to TiDB > Step 4. Tune the import performance (optional)`
- Source Line Ranges: `39-118`
- Source Scope: `self_managed`
- Primary Component: `lightning`
- Related Components: `pd`, `tidb`, `tikv`
- Topic Tags: `configuration`, `toml`, `backend`, `csv-format`, `strict-format`, `performance-tuning`, `parallel-import`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0116_e527330df2`
- Source ID: `tidb-docs-8.1:migrate-from-csv-files-to-tidb.md#step-3-create-the-configuration-file`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `106c305ccef01d65bff41459e7274e0f4422ce98baf6d8324330b785ff44a149`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/migrate-from-csv-files-to-tidb#step-3-create-the-configuration-file
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/migrate-from-csv-files-to-tidb.md

## Retrieval Guidance

- Use When: Use this chunk when you need the official `tidb-lightning.toml` settings for CSV import or the conditions and risks of enabling `strict-format` to parallelize a large CSV file import.
- Retrieval Keywords: tidb-lightning.toml, [tikv-importer], backend = "local", backend = "tidb", sorted-kv-dir, [mydumper], data-source-dir, [mydumper.csv], separator, delimiter, header, not-null, null = '\\N', backslash-escape, trim-last-separator, status-port, pd-addr, strict-format = true, terminator, 256 MiB, The delimiter is empty, Each field does not contain CR (\r) or LF (\n)
- Follow-up Guidance: The source next shows how to run `tidb-lightning`, monitor progress, and verify completion in the log.
- Classification Note: This is classified as configuration because the content provides the import configuration file fields and optional tuning parameters for CSV parsing and strict-format behavior.

## Official Source Content

## Step 3. Create the configuration file

Create a `tidb-lightning.toml` file with the following content:

```toml
[lightning]
# Log
level = "info"
file = "tidb-lightning.log"

[tikv-importer]
# "local": Default backend. The local backend is recommended to import large volumes of data (1 TiB or more). During the import, the target TiDB cluster cannot provide any service.
# "tidb": The "tidb" backend is recommended to import data less than 1 TiB. During the import, the target TiDB cluster can provide service normally.
# For more information on import mode, refer to <https://docs.pingcap.com/tidb/stable/tidb-lightning-overview#tidb-lightning-architecture>
backend = "local"
# Set the temporary storage directory for the sorted Key-Value files. The directory must be empty, and the storage space must be greater than the size of the dataset to be imported. For better import performance, it is recommended to use a directory different from `data-source-dir` and use flash storage, which can use I/O exclusively.
sorted-kv-dir = "/mnt/ssd/sorted-kv-dir"

[mydumper]
# Directory of the data source.
data-source-dir = "${data-path}" # A local path or S3 path. For example, 's3://my-bucket/sql-backup'.

# Defines CSV format.
[mydumper.csv]
# Field separator of the CSV file. Must not be empty. If the source file contains fields that are not string or numeric, such as binary, blob, or bit, it is recommended not to usesimple delimiters such as ",", and use an uncommon character combination like "|+|" instead.
separator = ','
# Delimiter. Can be zero or multiple characters.
delimiter = '"'
# Line terminator. By default, \r, \n, and \r\n are all treated as line terminators.
# terminator = "\r\n"
# Configures whether the CSV file has a table header.
# If this item is set to true, TiDB Lightning uses the first line of the CSV file to parse the corresponding relationship of fields.
header = true
# Configures whether the CSV file contains NULL.
# If this item is set to true, any column of the CSV file cannot be parsed as NULL.
not-null = false
# If `not-null` is set to false (CSV contains NULL),
# The following value is parsed as NULL.
null = '\N'
# Whether to treat the backslash ('\') in the string as an escape character.
backslash-escape = true
# Whether to trim the last separator at the end of each line.
trim-last-separator = false

[tidb]
# The target cluster.
host = ${host}            # e.g.: 172.16.32.1
port = ${port}            # e.g.: 4000
user = "${user_name}"     # e.g.: "root"
password = "${password}"  # e.g.: "rootroot"
status-port = ${status-port} # During the import, TiDB Lightning needs to obtain the table schema information from the TiDB status port. e.g.: 10080
pd-addr = "${ip}:${port}" # The address of the PD cluster, e.g.: 172.16.31.3:2379. TiDB Lightning obtains some information from PD. When backend = "local", you must specify status-port and pd-addr correctly. Otherwise, the import will be abnormal.
```

For more information on the configuration file, refer to [TiDB Lightning Configuration](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration).
## Step 4. Tune the import performance (optional)

When you import data from CSV files with a uniform size of about 256 MiB, TiDB Lightning works in the best performance. However, if you import data from a single large CSV file, TiDB Lightning can only use one thread to process the import by default, which might slow down the import speed.

To speed up the import, you can split a large CSV file into smaller ones. For a CSV file in a common format, before TiDB Lightning reads the entire file, it is hard to quickly locate the beginning and ending positions of each line. Therefore, TiDB Lightning does not automatically split CSV files by default. But if your CSV files to be imported meet certain format requirements, you can enable the `strict-format` mode. In this mode, TiDB Lightning automatically splits a single large CSV file into multiple files, each in about 256 MiB, and processes them in parallel.

> **Note:**
>
> If a CSV file is not in a strict format but the `strict-format` mode is set to `true` by mistake, a field that spans multiple lines will be split into two fields. This causes the parsing to fail, and TiDB Lightning might import the corrupted data without reporting any error.

In a strict-format CSV file, each field only takes up one line. It must meet the following requirements:

- The delimiter is empty.
- Each field does not contain CR (`\r`) or LF (`\n`).

You need to explicitly specify the line terminator `terminator` for a `strict-format` CSV file.

If your CSV file meets the above requirements, you can speed up the import by enabling the `strict-format` mode as follows:

```toml
[mydumper]
strict-format = true
```
