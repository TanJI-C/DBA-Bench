# TiDB Lightning import errors for character set and compression type

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-lightning/troubleshoot-tidb-lightning.md`
- Source Title: `Troubleshoot TiDB Lightning`
- Source Heading Path: `Troubleshoot TiDB Lightning > TiDB Lightning reports an error > `Unknown character set` | Troubleshoot TiDB Lightning > TiDB Lightning reports an error > `invalid compression type ...``
- Source Line Ranges: `185-195`
- Source Scope: `self_managed`
- Primary Component: `lightning`
- Related Components: `tidb`
- Topic Tags: `import-errors`, `character-set`, `compression`, `schema`, `data-files`, `compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0103_42c0715ad5`
- Source ID: `tidb-docs-8.1:tidb-lightning/troubleshoot-tidb-lightning.md#unknown-character-set`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `04bd9c520036c29ee74822161e005a009d6a824de028fab43fb6c2d86944fe46`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-lightning/troubleshoot-tidb-lightning#unknown-character-set
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-lightning/troubleshoot-tidb-lightning.md

## Retrieval Guidance

- Use When: Use this when TiDB Lightning import fails with `Unknown character set` during schema creation or with `invalid compression type ...` while scanning compressed source data files.
- Retrieval Keywords: TiDB Lightning `Unknown character set`, TiDB does not support all MySQL character sets, character sets supported by TiDB, create the table schema in the downstream in advance, TiDB Lightning `invalid compression type ...`, compressed data files `gzip` `snappy` `zstd`, unsupported compressed file exists in the directory where the source data file is stored, move unsupported files out of the import data directory, official Snappy format, Compressed files
- Follow-up Guidance: The content notes that supported compressed data files are `gzip`, `snappy`, and `zstd`, and that Snappy files must be in the official Snappy format.
- Classification Note: This is classified as diagnosis for TiDB Lightning because the content explains two reported import errors and the specific compatibility conditions that trigger them.

## Official Source Content

### `Unknown character set`

TiDB does not support all MySQL character sets. Therefore, TiDB Lightning reports this error if an unsupported character set is used when creating the table schema during an import. To bypass this error, you can create the table schema in the downstream in advance using the [character sets supported by TiDB](https://docs.pingcap.com/tidb/stable/character-set-and-collation) according to the specific data.
### `invalid compression type ...`

- TiDB Lightning v6.4.0 and later versions only support the following compressed data files: `gzip`, `snappy`, and `zstd`. Other types of compressed files cause errors. If an unsupported compressed file exists in the directory where the source data file is stored, this will cause the task to report an error. You can move those unsupported files out of the import data directory to avoid such errors. For more details, see [Compressed files](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-data-source#compressed-files).

> **Note:**
>
> The Snappy compressed file must be in the [official Snappy format](https://github.com/google/snappy). Other variants of Snappy compression are not supported.
