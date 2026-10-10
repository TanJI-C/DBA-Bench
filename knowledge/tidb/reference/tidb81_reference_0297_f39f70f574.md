# Encryption and compression functions overview

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/encryption-and-compression-functions.md`
- Source Title: `Encryption and Compression Functions`
- Source Heading Path: `Encryption and Compression Functions | Encryption and Compression Functions > Supported functions`
- Source Line Ranges: `5-27`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: none
- Topic Tags: `encryption`, `compression`, `hashing`, `password`, `random-bytes`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0297_f39f70f574`
- Source ID: `tidb-docs-8.1:functions-and-operators/encryption-and-compression-functions.md#encryption-and-compression-functions`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a6d2d2b39e4053798cf690a9b4bf38d1207d4749400da737b53eb2969fd91e51`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/encryption-and-compression-functions#encryption-and-compression-functions
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/encryption-and-compression-functions.md

## Retrieval Guidance

- Use When: Use this chunk when you need the supported TiDB SQL encryption and compression function list or want to confirm whether a specific function is available.
- Retrieval Keywords: Encryption and Compression Functions, Supported functions, AES_DECRYPT(), AES_ENCRYPT(), COMPRESS(), MD5(), PASSWORD(), RANDOM_BYTES(), SHA(), SHA1(), SHA2(), SM3(), UNCOMPRESS(), UNCOMPRESSED_LENGTH(), VALIDATE_PASSWORD_STRENGTH()
- Follow-up Guidance: If the user asks about one listed function such as AES, COMPRESS, MD5, PASSWORD, RANDOM_BYTES, SHA, or SHA2, retrieve the corresponding function-specific section.
- Classification Note: This is a reference overview because the content is a support matrix of function names and short descriptions under SQL encryption and compression functions.

## Official Source Content

# Encryption and Compression Functions

TiDB supports most of the [encryption and compression functions](https://dev.mysql.com/doc/refman/8.0/en/encryption-functions.html) available in MySQL 8.0.
## Supported functions

| Name                                                          | Description                                       |
|:--------------------------------------------------------------|:--------------------------------------------------|
| [`AES_DECRYPT()`](#aes_decrypt)                               | Decrypt using AES                                 |
| [`AES_ENCRYPT()`](#aes_encrypt)                               | Encrypt using AES                                 |
| [`COMPRESS()`](#compress)                                     | Compress and return result as a binary string     |
| [`MD5()`](#md5)                                               | Calculate MD5 checksum                            |
| [`PASSWORD()`](#password)                                     | Calculate and return a password string            |
| [`RANDOM_BYTES()`](#random_bytes)                             | Return a random byte vector                       |
| [`SHA()`](#sha)                                               | Calculate an SHA-1 160-bit checksum               |
| [`SHA1()`](#sha1)                                             | Calculate an SHA-1 160-bit checksum               |
| [`SHA2()`](#sha2)                                             | Calculate an SHA-2 checksum                       |
| [`SM3()`](#sm3)                                               | Calculate an SM3 checksum                         |
| [`UNCOMPRESS()`](#uncompress)                                 | Uncompress a compressed string                    |
| [`UNCOMPRESSED_LENGTH()`](#uncompressed_length)               | Return the length of a string before compression  |
| [`VALIDATE_PASSWORD_STRENGTH()`](#validate_password_strength) | Validate the password strength                    |
