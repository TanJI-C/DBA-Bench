# SM3 hash and compression utility functions

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/encryption-and-compression-functions.md`
- Source Title: `Encryption and Compression Functions`
- Source Heading Path: `Encryption and Compression Functions > Supported functions > `SM3()` | Encryption and Compression Functions > Supported functions > [`UNCOMPRESS()`](https://dev.mysql.com/doc/refman/8.0/en/encryption-functions.html#function_uncompress) | Encryption and Compression Functions > Supported functions > [`UNCOMPRESSED_LENGTH()`](https://dev.mysql.com/doc/refman/8.0/en/encryption-functions.html#function_uncompressed-length)`
- Source Line Ranges: `229-283`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `hash-functions`, `sm3`, `compression`, `decompression`, `string-functions`, `examples`, `mysql-compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0302_ad62a9a4a5`
- Source ID: `tidb-docs-8.1:functions-and-operators/encryption-and-compression-functions.md#sm3`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e40ddc8027e48d2c5630a843f07636f9fd15e36b27f07448add4494b9ed3db7a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/encryption-and-compression-functions#sm3
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/encryption-and-compression-functions.md

## Retrieval Guidance

- Use When: Use this chunk when looking up the SQL functions `SM3()`, `UNCOMPRESS()`, or `UNCOMPRESSED_LENGTH()` and their documented behavior and examples.
- Retrieval Keywords: SM3(), SM3(str), ShangMi 3, 256-bit hash, TiDB extension, not implemented in MySQL, UNCOMPRESS(), UNCOMPRESS(data), decompresses data compressed with COMPRESS(), UNCOMPRESSED_LENGTH(), UNCOMPRESSED_LENGTH(data), first 4 bytes of compressed data, compressed string length before COMPRESS()
- Follow-up Guidance: The examples show `SELECT SM3('abc');`, `SELECT UNCOMPRESS(0x03000000789C72747206040000FFFF018D00C7);`, and `SELECT UNCOMPRESSED_LENGTH(0x03000000789C72747206040000FFFF018D00C7);`.
- Classification Note: This is reference content because it defines supported SQL encryption and compression utility functions and shows exact example statements and outputs.

## Official Source Content

### `SM3()`

> **Note:**
>
> The `SM3()` function is a TiDB extension and is not implemented in MySQL.

The `SM3(str)` function calculates a 256-bit [ShangMi 3 (SM3)](https://en.wikipedia.org/wiki/SM3_(hash_function)) hash for the given argument `str`.

```sql
SELECT SM3('abc');
```

```
+------------------------------------------------------------------+
| SM3('abc')                                                       |
+------------------------------------------------------------------+
| 66c7f0f462eeedd9d1f2d46bdc10e4e24167c4875cf2f7a2297da02b8f4ba8e0 |
+------------------------------------------------------------------+
1 row in set (0.00 sec)
```
### [`UNCOMPRESS()`](https://dev.mysql.com/doc/refman/8.0/en/encryption-functions.html#function_uncompress)

The `UNCOMPRESS(data)` function decompresses the data that was compressed with the [`COMPRESS()`](#compress) function.

```sql
SELECT UNCOMPRESS(0x03000000789C72747206040000FFFF018D00C7);
```

```
+------------------------------------------------------------------------------------------------------------+
| UNCOMPRESS(0x03000000789C72747206040000FFFF018D00C7)                                                       |
+------------------------------------------------------------------------------------------------------------+
| 0x414243                                                                                                   |
+------------------------------------------------------------------------------------------------------------+
1 row in set (0.00 sec)
```
### [`UNCOMPRESSED_LENGTH()`](https://dev.mysql.com/doc/refman/8.0/en/encryption-functions.html#function_uncompressed-length)

The `UNCOMPRESSED_LENGTH(data)` function returns the first 4 bytes of the compressed data, which store the length that the compressed string had before being compressed with the [`COMPRESS()`](#compress) function.

```sql
SELECT UNCOMPRESSED_LENGTH(0x03000000789C72747206040000FFFF018D00C7);
```

```
+---------------------------------------------------------------+
| UNCOMPRESSED_LENGTH(0x03000000789C72747206040000FFFF018D00C7) |
+---------------------------------------------------------------+
|                                                             3 |
+---------------------------------------------------------------+
1 row in set (0.00 sec)
```
