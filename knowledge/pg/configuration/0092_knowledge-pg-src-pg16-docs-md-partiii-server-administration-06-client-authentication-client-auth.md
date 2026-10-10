# An Example pg_ident.conf File

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/06_client_authentication.md`
- Source Title: `Client Authentication`
- Source Heading Path: `Client Authentication > An Example pg_ident.conf File`
- Source Line Ranges: `763-765`
- Chunk ID: `pg16_configuration_0092_0c235771cf`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5661b4b8a644ebea531984c9be343434803f7da1cc2cb4468931b5a81362e424`

## Retrieval Guidance

- Use When: 需要理解 pg_ident.conf 多条映射如何允许/拒绝连接身份。
- Retrieval Keywords: pg_ident example, omicron, bryanh, ann, robert, guest1
- Follow-up Guidance: 结合 HBA 中 ident map=omicron 使用。
- Classification Note: 给出 omicron map 下系统用户到数据库用户的具体映射示例。

## Official Source Content

## An Example `pg_ident.conf` File

```
