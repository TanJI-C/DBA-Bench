# MD5 and PASSWORD hashes

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/encryption-and-compression-functions.md`
- Source Title: `Encryption and Compression Functions`
- Source Heading Path: `Encryption and Compression Functions > Supported functions > [`MD5()`](https://dev.mysql.com/doc/refman/8.0/en/encryption-functions.html#function_md5) | Encryption and Compression Functions > Supported functions > [`PASSWORD()`](https://dev.mysql.com/doc/refman/5.7/en/encryption-functions.html#function_password)`
- Source Line Ranges: `124-163`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: none
- Topic Tags: `md5`, `password hash`, `deprecated`, `mysql_native_password`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0300_1ea7c8834b`
- Source ID: `tidb-docs-8.1:functions-and-operators/encryption-and-compression-functions.md#md5-https-dev-mysql-com-doc-refman-8-0-en-encryption-functions-html-function-md5`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `448c79d435904b494de7685fff468461fc09bdd78171d4cbdb5fc92172d3da72`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/encryption-and-compression-functions#md5-https-dev-mysql-com-doc-refman-8-0-en-encryption-functions-html-function-md5
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/encryption-and-compression-functions.md

## Retrieval Guidance

- Use When: Use this chunk when the query asks about MD5(expr), PASSWORD(str), mysql_native_password hashes, or the deprecation warning for PASSWORD().
- Retrieval Keywords: MD5(expr), 128-bit MD5 hash, SELECT MD5('abc'), PASSWORD(str), mysql_native_password, PASSWORD is deprecated, Warning (Code 1681): PASSWORD is deprecated and will be removed in a future release, SELECT PASSWORD('secret')
- Follow-up Guidance: The content says PASSWORD(str) calculates a password hash usable with the mysql_native_password authentication method and shows that executing it returns a deprecation warning.
- Classification Note: This is a reference section because it documents two hash-related SQL functions, including PASSWORD() deprecation status from the official content.

## Official Source Content

### [`MD5()`](https://dev.mysql.com/doc/refman/8.0/en/encryption-functions.html#function_md5)

The `MD5(expr)` function calculates a 128-bit [MD5](https://en.wikipedia.org/wiki/MD5) hash for the given argument `expr`.

```sql
SELECT MD5('abc');
```

```
+----------------------------------+
| MD5('abc')                       |
+----------------------------------+
| 900150983cd24fb0d6963f7d28e17f72 |
+----------------------------------+
1 row in set (0.00 sec)
```
### [`PASSWORD()`](https://dev.mysql.com/doc/refman/5.7/en/encryption-functions.html#function_password)

> **Warning:**
>
> This function is deprecated in MySQL 5.7 and removed in MySQL 8.0. It is deprecated in TiDB. It is not recommended to use this function.

The `PASSWORD(str)` function calculates a password hash that can be used with the `mysql_native_password` authentication method.

```sql
SELECT PASSWORD('secret');
```

```
+-------------------------------------------+
| PASSWORD('secret')                        |
+-------------------------------------------+
| *14E65567ABDB5135D0CFD9A70B3032C179A49EE7 |
+-------------------------------------------+
1 row in set, 1 warning (0.00 sec)

Warning (Code 1681): PASSWORD is deprecated and will be removed in a future release.
```
