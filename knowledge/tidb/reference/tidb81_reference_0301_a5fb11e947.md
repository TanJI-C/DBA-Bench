# Random bytes and SHA hashes

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/encryption-and-compression-functions.md`
- Source Title: `Encryption and Compression Functions`
- Source Heading Path: `Encryption and Compression Functions > Supported functions > [`RANDOM_BYTES()`](https://dev.mysql.com/doc/refman/8.0/en/encryption-functions.html#function_random-bytes) | Encryption and Compression Functions > Supported functions > [`SHA()`](https://dev.mysql.com/doc/refman/8.0/en/encryption-functions.html#function_sha1) | Encryption and Compression Functions > Supported functions > [`SHA1()`](https://dev.mysql.com/doc/refman/8.0/en/encryption-functions.html#function_sha1) | Encryption and Compression Functions > Supported functions > [`SHA2()`](https://dev.mysql.com/doc/refman/8.0/en/encryption-functions.html#function_sha2)`
- Source Line Ranges: `164-228`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: none
- Topic Tags: `random bytes`, `sha1`, `sha2`, `hashing`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0301_a5fb11e947`
- Source ID: `tidb-docs-8.1:functions-and-operators/encryption-and-compression-functions.md#random-bytes-https-dev-mysql-com-doc-refman-8-0-en-encryption-functions-html-function-random-bytes`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5c62e6a8df8934cdf6fcf2b2d1434ef4df5ea57bd366e80ccbcfe3df18b1945e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/encryption-and-compression-functions#random-bytes-https-dev-mysql-com-doc-refman-8-0-en-encryption-functions-html-function-random-bytes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/encryption-and-compression-functions.md

## Retrieval Guidance

- Use When: Use this chunk when the query asks about RANDOM_BYTES(n), the alias relationship between SHA() and SHA1(), or supported SHA2(str, n) algorithms and NULL behavior.
- Retrieval Keywords: RANDOM_BYTES(n), SELECT RANDOM_BYTES(3), SHA(), SHA1(), SHA() is an alias for SHA1, SHA1(expr), 160-bit SHA-1 hash, SELECT SHA1('abc'), SHA2(str, n), supported algorithms, SHA-224, SHA-256, SHA-384, SHA-512, SHA2 returns NULL if any arguments are NULL or algorithm is unknown or unsupported, SELECT SHA2('abc',224)
- Follow-up Guidance: This chunk includes the SHA2() algorithm mapping for n values 0, 224, 256, 384, and 512.
- Classification Note: This is a reference section because it defines random byte and hash SQL functions, their aliasing, supported SHA-2 algorithm selectors, and examples.

## Official Source Content

### [`RANDOM_BYTES()`](https://dev.mysql.com/doc/refman/8.0/en/encryption-functions.html#function_random-bytes)

The `RANDOM_BYTES(n)` function returns `n` random bytes.

```sql
SELECT RANDOM_BYTES(3);
```

```
+----------------------------------+
| RANDOM_BYTES(3)                  |
+----------------------------------+
| 0x1DBC0D                         |
+----------------------------------+
1 row in set (0.00 sec)
```
### [`SHA()`](https://dev.mysql.com/doc/refman/8.0/en/encryption-functions.html#function_sha1)

The `SHA()` function is an alias for [`SHA1`](#sha1).
### [`SHA1()`](https://dev.mysql.com/doc/refman/8.0/en/encryption-functions.html#function_sha1)

The `SHA1(expr)` function calculates a 160-bit [SHA-1](https://en.wikipedia.org/wiki/SHA-1) hash for the given argument `expr`.

```sql
SELECT SHA1('abc');
```

```
+------------------------------------------+
| SHA1('abc')                              |
+------------------------------------------+
| a9993e364706816aba3e25717850c26c9cd0d89d |
+------------------------------------------+
1 row in set (0.00 sec)
```
### [`SHA2()`](https://dev.mysql.com/doc/refman/8.0/en/encryption-functions.html#function_sha2)

The `SHA2(str, n)` function calculates a hash using an algorithm from the [SHA-2](https://en.wikipedia.org/wiki/SHA-2) family. The `n` argument is used to select the algorithm. `SHA2()` returns `NULL` if any of the arguments are `NULL` or if the algorithm selected by `n` is unknown or unsupported.

The following lists supported algorithms:

| n   | Algorithm |
|-----|-----------|
| 0   | SHA-256   |
| 224 | SHA-224   |
| 256 | SHA-256   |
| 384 | SHA-384   |
| 512 | SHA-512   |

```sql
SELECT SHA2('abc',224);
```

```
+----------------------------------------------------------+
| SHA2('abc',224)                                          |
+----------------------------------------------------------+
| 23097d223405d8228642a477bda255b32aadbce4bda0b3f7e36c9da7 |
+----------------------------------------------------------+
1 row in set (0.00 sec)
```
