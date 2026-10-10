# Unsupported encryption functions and MySQL compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/encryption-and-compression-functions.md`
- Source Title: `Encryption and Compression Functions`
- Source Heading Path: `Encryption and Compression Functions > Unsupported functions | Encryption and Compression Functions > MySQL compatibility`
- Source Line Ranges: `420-428`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `unsupported-functions`, `mysql-compatibility`, `aes`, `statement-digest`, `sm3`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0304_543f8ec3c3`
- Source ID: `tidb-docs-8.1:functions-and-operators/encryption-and-compression-functions.md#unsupported-functions`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2857d629ad44dd3afc3f6debb558e9a303c144d59532ae4ce5b4a4b45350d7a8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/encryption-and-compression-functions#unsupported-functions
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/encryption-and-compression-functions.md

## Retrieval Guidance

- Use When: Use this chunk when checking unsupported encryption-related functions and MySQL compatibility differences for `STATEMENT_DIGEST()`, `STATEMENT_DIGEST_TEXT()`, `AES_ENCRYPT()`, `AES_DECRYPT`, and `SM3()`.
- Retrieval Keywords: Unsupported functions, MySQL compatibility, STATEMENT_DIGEST(), STATEMENT_DIGEST_TEXT(), AES_ENCRYPT(), AES_DECRYPT, kdf_name, salt, iterations, MySQL 8.0.30, functions only available in MySQL Enterprise, Issue #2632, MySQL does not implement SM3(), TiDB does not support
- Follow-up Guidance: This chunk points to compatibility limits: TiDB does not support MySQL Enterprise-only functions, does not support `STATEMENT_DIGEST()` or `STATEMENT_DIGEST_TEXT()`, does not support the `kdf_name`, `salt`, and `iterations` arguments for `AES_ENCRYPT()` and `AES_DECRYPT`, and notes that MySQL does not implement `SM3()`.
- Classification Note: This is reference content because it lists explicit unsupported functions and argument compatibility differences between TiDB and MySQL.

## Official Source Content

## Unsupported functions

* TiDB does not support the functions only available in MySQL Enterprise [Issue #2632](https://github.com/pingcap/tidb/issues/2632).
## MySQL compatibility

* TiDB does not support the `STATEMENT_DIGEST()` and `STATEMENT_DIGEST_TEXT()` functions.
* TiDB does not support the `kdf_name`, `salt`, and `iterations` arguments for [`AES_ENCRYPT()`](#aes_encrypt) and [`AES_DECRYPT`](#aes_decrypt) that MySQL added in MySQL 8.0.30.
* MySQL does not implement the [`SM3()`](#sm3) function.
