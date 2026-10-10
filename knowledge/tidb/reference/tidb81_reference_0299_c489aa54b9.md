# Compression function COMPRESS

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/encryption-and-compression-functions.md`
- Source Title: `Encryption and Compression Functions`
- Source Heading Path: `Encryption and Compression Functions > Supported functions > [`COMPRESS()`](https://dev.mysql.com/doc/refman/8.0/en/encryption-functions.html#function_compress)`
- Source Line Ranges: `70-123`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: none
- Topic Tags: `compression`, `zlib`, `binary string`, `length`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0299_c489aa54b9`
- Source ID: `tidb-docs-8.1:functions-and-operators/encryption-and-compression-functions.md#compress-https-dev-mysql-com-doc-refman-8-0-en-encryption-functions-html-function-compress`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a76eba60e7e660aabb16e2270acef583caa5aeef0104723afd87fd5f096728cb`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/encryption-and-compression-functions#compress-https-dev-mysql-com-doc-refman-8-0-en-encryption-functions-html-function-compress
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/encryption-and-compression-functions.md

## Retrieval Guidance

- Use When: Use this chunk when the query asks how COMPRESS(expr) formats its binary output, handles NULL or empty strings, or uses zlib-compressed data with an uncompressed length prefix.
- Retrieval Keywords: COMPRESS(expr), compressed version of input data, binary string, Bytes 0 to 3: the uncompressed length, Bytes 4 to the end: the zlib compressed data, NULL returns NULL, empty string returns a zero-length value, SELECT COMPRESS(0x414243), LENGTH(COMPRESS(a)), zlib
- Follow-up Guidance: The chunk also includes an example showing how to decode the COMPRESS() result outside of TiDB using Python and zlib, and a length comparison example for REPEAT('a',100).
- Classification Note: This is a reference entry because it specifies COMPRESS() return rules, output structure, and concrete SQL examples.

## Official Source Content

### [`COMPRESS()`](https://dev.mysql.com/doc/refman/8.0/en/encryption-functions.html#function_compress)

The `COMPRESS(expr)` function returns a compressed version of the input data `expr`.

- If the argument is `NULL`, the function returns `NULL`.
- If the argument is an empty string, the function returns a zero-length value.

For non-zero length argument, the function returns a binary string with the following structure:

- Bytes 0 to 3: the uncompressed length
- Bytes 4 to the end: the zlib compressed data

```sql
SELECT COMPRESS(0x414243);
```

```
+------------------------------------------+
| COMPRESS(0x414243)                       |
+------------------------------------------+
| 0x03000000789C72747206040000FFFF018D00C7 |
+------------------------------------------+
1 row in set (0.00 sec)
```

In this output, `0x03000000` represents the uncompressed length (3) and `0x789C72747206040000FFFF018D00C7` is the zlib compressed data.

An example of using Python to decode this outside of TiDB:

```python
import codecs
import zlib

data = codecs.decode('03000000789C72747206040000FFFF018D00C7','hex')
print(int.from_bytes(data[:4], byteorder='little'))  # 3
print(zlib.decompress(data[4:]))  # b'ABC'
```

For short strings, `COMPRESS()` might return more bytes than the input. The following example shows that a string of 100 `a` characters compresses to 19 bytes.

```sql
WITH x AS (SELECT REPEAT('a',100) 'a')
SELECT LENGTH(a),LENGTH(COMPRESS(a)) FROM x;
```

```
+-----------+---------------------+
| LENGTH(a) | LENGTH(COMPRESS(a)) |
+-----------+---------------------+
|       100 |                  19 |
+-----------+---------------------+
1 row in set (0.00 sec)
```
