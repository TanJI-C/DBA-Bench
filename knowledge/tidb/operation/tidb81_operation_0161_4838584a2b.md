# Run CSV import, verify progress, and adapt other flat file formats

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/migrate-from-csv-files-to-tidb.md`
- Source Title: `Migrate Data from CSV Files to TiDB`
- Source Heading Path: `Migrate Data from CSV Files to TiDB > Step 5. Import the data | Migrate Data from CSV Files to TiDB > Other file formats | Migrate Data from CSV Files to TiDB > What's next`
- Source Line Ranges: `119-189`
- Source Scope: `self_managed`
- Primary Component: `lightning`
- Related Components: `tiup`
- Topic Tags: `import-execution`, `nohup`, `progress-monitoring`, `log-verification`, `troubleshooting`, `tsv`, `file-formats`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0161_4838584a2b`
- Source ID: `tidb-docs-8.1:migrate-from-csv-files-to-tidb.md#step-5-import-the-data`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `afeaf2426afc73d5a167e9f35ad83b2d71d7344c8f453da5ba33e6b739fec60d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/migrate-from-csv-files-to-tidb#step-5-import-the-data
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/migrate-from-csv-files-to-tidb.md

## Retrieval Guidance

- Use When: Use this chunk when you need the documented command to start a CSV import, the supported ways to check TiDB Lightning progress, the success log message, or example `[mydumper.csv]` settings for TSV and TPC-H DBGEN files.
- Retrieval Keywords: nohup tiup tidb-lightning -config tidb-lightning.toml > nohup.out 2>&1 &, grep the keyword progress, monitoring dashboard, TiDB Lightning web interface, the whole procedure completed, tidb lightning exit, TiDB Lightning FAQ, Other file formats, .csv, TSV, separator = "\t", delimiter = '', null = 'NULL', TPC-H DBGEN, separator = '|', trim-last-separator = true, CSV Support and Restrictions
- Follow-up Guidance: The source points to `CSV Support and Restrictions` for more information after the import examples.
- Classification Note: This is classified as operation because the content describes running the import process, monitoring and validating its outcome, and adapting configuration for other flat file formats.

## Official Source Content

## Step 5. Import the data

To start the import, run `tidb-lightning`. If you launch the program in the command line, the process might exit unexpectedly after receiving a SIGHUP signal. In this case, it is recommended to run the program using a `nohup` or `screen` tool. For example:

```shell
nohup tiup tidb-lightning -config tidb-lightning.toml > nohup.out 2>&1 &
```

After the import starts, you can check the progress of the import by either of the following methods:

- `grep` the keyword `progress` in the log. The progress is updated every 5 minutes by default.
- Check progress in [the monitoring dashboard](https://docs.pingcap.com/tidb/stable/tidb-lightning/monitor-tidb-lightning).
- Check progress in [the TiDB Lightning web interface](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-web-interface).

After TiDB Lightning completes the import, it exits automatically. Check whether `tidb-lightning.log` contains `the whole procedure completed` in the last lines. If yes, the import is successful. If no, the import encounters an error. Address the error as instructed in the error message.

> **Note:**
>
> Whether the import is successful or not, the last line of the log shows `tidb lightning exit`. It means that TiDB Lightning exits normally, but does not necessarily mean that the import is successful.

If the import fails, refer to [TiDB Lightning FAQ](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-faq) for troubleshooting.
## Other file formats

If your data source is in other formats, to migrate data from your data source, you must end the file name with `.csv` and make corresponding changes in the `[mydumper.csv]` section of the `tidb-lightning.toml` configuration file. Here are example changes for common formats:

**TSV:**

```toml
# Format example
# ID    Region    Count
# 1     East      32
# 2     South     NULL
# 3     West      10
# 4     North     39

# Format configuration
[mydumper.csv]
separator = "\t"
delimiter = ''
header = true
not-null = false
null = 'NULL'
backslash-escape = false
trim-last-separator = false
```

**TPC-H DBGEN:**

```toml
# Format example
# 1|East|32|
# 2|South|0|
# 3|West|10|
# 4|North|39|

# Format configuration
[mydumper.csv]
separator = '|'
delimiter = ''
header = false
not-null = true
backslash-escape = false
trim-last-separator = true
```
## What's next

- [CSV Support and Restrictions](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-data-source#csv).
