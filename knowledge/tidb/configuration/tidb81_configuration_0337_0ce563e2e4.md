# CSV strict format, examples, and SQL file sizing

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-lightning/tidb-lightning-data-source.md`
- Source Title: `TiDB Lightning Data Sources`
- Source Heading Path: `TiDB Lightning Data Sources > CSV > Strict format | TiDB Lightning Data Sources > CSV > Common configuration examples | TiDB Lightning Data Sources > CSV > Common configuration examples > CSV | TiDB Lightning Data Sources > CSV > Common configuration examples > TSV | TiDB Lightning Data Sources > CSV > Common configuration examples > TPC-H DBGEN | TiDB Lightning Data Sources > SQL`
- Source Line Ranges: `251-341`
- Source Scope: `self_managed`
- Primary Component: `lightning`
- Related Components: `sql`
- Topic Tags: `csv`, `strict-format`, `parallelism`, `file-splitting`, `configuration`, `examples`, `tsv`, `tpch`, `sql-files`, `file-sizing`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0337_0ce563e2e4`
- Source ID: `tidb-docs-8.1:tidb-lightning/tidb-lightning-data-source.md#strict-format`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0a3c294a8864ebebaf7d7bfad2303338665e3dee2bf082913bd9d84296e03e9b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-data-source#strict-format
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-lightning/tidb-lightning-data-source.md

## Retrieval Guidance

- Use When: Use this chunk when you need TiDB Lightning CSV strict-format requirements, example CSV or TSV or TPC-H DBGEN mydumper.csv settings, or guidance about single huge CSV or SQL files and the around 256 MiB file size.
- Retrieval Keywords: strict-format, [mydumper] strict-format = true, CSV strict format, uniform size around 256 MiB, single huge CSV file one thread, split CSV into multiple 256 MiB-sized chunks, CR \r, LF \n, RFC 4180, [mydumper.csv], separator, delimiter, header, not-null, null, backslash-escape, TSV, TPC-H DBGEN, terminator = "|\n", single huge SQL file, cannot quickly split a single SQL file
- Follow-up Guidance: If strict-format is wrongly set to true for a non-strict CSV file, a field spanning multiple lines may be cut into two chunks, causing parse failure or corrupted data.
- Classification Note: The classification is configuration because the content defines mydumper and mydumper.csv settings and format constraints that control how TiDB Lightning reads CSV, TSV, TPC-H DBGEN, and SQL input files.

## Official Source Content

### Strict format

TiDB Lightning works best when the input files have a uniform size of around 256 MiB. When the input is a single huge CSV file, TiDB Lightning can only process the file in one thread, which slows down the import speed.

This can be fixed by splitting the CSV into multiple files first. For the generic CSV format, there is no way to quickly identify where a row starts or ends without reading the whole file. Therefore, TiDB Lightning by default does *not* automatically split a CSV file. However, if you are certain that the CSV input adheres to certain restrictions, you can enable the `strict-format` setting to allow TiDB Lightning to split the file into multiple 256 MiB-sized chunks for parallel processing.

```toml
[mydumper]
strict-format = true
```

In a strict CSV file, every field occupies only a single line. In other words, one of the following must be true:

* Delimiter is empty.
* Every field does not contain the terminator itself. In the default configuration, this means every field does not contain CR (`\r`) or LF (`\n`).

If a CSV file is not strict, but `strict-format` is wrongly set to `true`, a field spanning multiple lines may be cut in half into two chunks, causing parse failure, or even quietly importing corrupted data.
### Common configuration examples
#### CSV

The default setting is already tuned for CSV following RFC 4180.

```toml
[mydumper.csv]
separator = ',' # If the data might contain a comma (','), it is recommended to use '|+|' or other uncommon character combinations as the separator.
delimiter = '"'
header = true
not-null = false
null = '\N'
backslash-escape = true
```

Example content:

```
ID,Region,Count
1,"East",32
2,"South",\N
3,"West",10
4,"North",39
```
#### TSV

```toml
[mydumper.csv]
separator = "\t"
delimiter = ''
header = true
not-null = false
null = 'NULL'
backslash-escape = false
```

Example content:

```
ID    Region    Count
1     East      32
2     South     NULL
3     West      10
4     North     39
```
#### TPC-H DBGEN

```toml
[mydumper.csv]
separator = '|'
delimiter = ''
terminator = "|\n"
header = false
not-null = true
backslash-escape = false
```

Example content:

```
1|East|32|
2|South|0|
3|West|10|
4|North|39|
```
## SQL

When TiDB Lightning processes a SQL file, because TiDB Lightning cannot quickly split a single SQL file, it cannot improve the import speed of a single file by increasing concurrency. Therefore, when you import data from SQL files, avoid a single huge SQL file. TiDB Lightning works best when the input files have a uniform size of around 256 MiB.
