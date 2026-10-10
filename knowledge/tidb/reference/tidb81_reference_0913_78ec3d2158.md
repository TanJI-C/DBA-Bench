# FAQ for local file import to TiDB Cloud Serverless

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tidb-cloud-import-local-files.md`
- Source Title: `Import Local Files to TiDB Cloud Serverless`
- Source Heading Path: `Import Local Files to TiDB Cloud Serverless > FAQ | Import Local Files to TiDB Cloud Serverless > FAQ > Can I only import some specified columns by the Import feature in TiDB Cloud? | Import Local Files to TiDB Cloud Serverless > FAQ > Why can't I query a column with a reserved keyword after importing data into TiDB Cloud? | Import Local Files to TiDB Cloud Serverless > FAQ > How to import a local file larger than 250 MiB?`
- Source Line Ranges: `84-140`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `sql`, `shared`
- Topic Tags: `faq`, `column-selection`, `load-data`, `reserved-keywords`, `backticks`, `large-files`, `cli`, `file-splitting`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0913_78ec3d2158`
- Source ID: `tidb-docs-8.1:tidb-cloud/tidb-cloud-import-local-files.md#faq`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6d9ddf49173bee8552f114220bcb1e1583455a47d8bacdc192eb50357451fd74`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-import-local-files#faq
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tidb-cloud-import-local-files.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks about local file import FAQ topics such as importing only selected columns, querying reserved keyword column names, large files over 250 MiB, or the LOAD DATA LOCAL INFILE access restriction error.
- Retrieval Keywords: FAQ, Can I only import some specified columns by the Import feature in TiDB Cloud?, LOAD DATA, LOAD DATA LOCAL INFILE, ERROR 2068 (HY000): LOAD DATA LOCAL INFILE file request rejected due to restrictions on access., --local-infile=true, reserved keyword, backticks, `order`, How to import a local file larger than 250 MiB?, TiDB Cloud CLI, ticloud serverless import start, split -l, split.sh
- Follow-up Guidance: The source provides an example CREATE TABLE statement, a LOAD DATA LOCAL INFILE example, and a shell script that splits a large CSV file into equal parts while preserving the file extension.
- Classification Note: This chunk is classified as reference because the official content is organized as FAQ answers and examples for specific import-related questions and errors.

## Official Source Content

## FAQ
### Can I only import some specified columns by the Import feature in TiDB Cloud?

No. Currently, you can only import all columns of a CSV file into an existing table when using the Import feature.

To import only some specified columns, you can use the MySQL client to connect your TiDB cluster, and then use [`LOAD DATA`](https://docs.pingcap.com/tidb/stable/sql-statement-load-data) to specify the columns to be imported. For example:

```sql
CREATE TABLE `import_test` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  `address` varchar(64) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB;
LOAD DATA LOCAL INFILE 'load.txt' INTO TABLE import_test FIELDS TERMINATED BY ',' (name, address);
```

If you use `mysql` and encounter `ERROR 2068 (HY000): LOAD DATA LOCAL INFILE file request rejected due to restrictions on access.`, you can add `--local-infile=true` in the connection string.
### Why can't I query a column with a reserved keyword after importing data into TiDB Cloud?

If a column name is a reserved [keyword](https://docs.pingcap.com/tidb/stable/keywords) in TiDB, when you query the column, you need to add backticks `` ` `` to enclose the column name. For example, if the column name is `order`, you need to query the column with `` `order` ``.
### How to import a local file larger than 250 MiB?

If the file is larger than 250 MiB, you can use [TiDB Cloud CLI](https://docs.pingcap.com/tidb/stable/tidb-cloud/get-started-with-cli) to import the file. For more information, see [`ticloud serverless import start`](https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-import-start).

Alternatively, you can use the `split [-l ${line_count}]` utility to split it into multiple smaller files (for Linux or macOS only). For example, run `split -l 100000 tidb-01.csv small_files` to split a file named `tidb-01.csv` by line length `100000`, and the split files are named `small_files${suffix}`. Then, you can import these smaller files to TiDB Cloud one by one.

Refer to the following script:

```bash
#!/bin/bash
n=$1
file_path=$2
file_extension="${file_path##*.}"
file_name="${file_path%.*}"
total_lines=$(wc -l < $file_path)
lines_per_file=$(( (total_lines + n - 1) / n ))
split -d -a 1 -l $lines_per_file $file_path $file_name.
for (( i=0; i<$n; i++ ))
do
    mv $file_name.$i $file_name.$i.$file_extension
done
```

You can input `n` and a file name, and then run the script. The script will divide the file into `n` equal parts while keeping the original file extension. For example:

```bash
> sh ./split.sh 3 mytest.customer.csv
> ls -h | grep mytest
mytest.customer.0.csv
mytest.customer.1.csv
mytest.customer.2.csv
mytest.customer.csv
```
