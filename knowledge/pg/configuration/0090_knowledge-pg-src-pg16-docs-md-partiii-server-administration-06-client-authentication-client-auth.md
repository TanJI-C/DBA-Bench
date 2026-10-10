# Example pg_hba.conf Entries

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/06_client_authentication.md`
- Source Title: `Client Authentication`
- Source Heading Path: `Client Authentication > Example pg_hba.conf Entries`
- Source Line Ranges: `528-530`
- Chunk ID: `pg16_configuration_0090_02d198dd60`
- Review Status: `needs_human_review`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b6ecfe0a04d84d77e7af435319ee41f75b4d1af6e15dca99e00b5e6b53c1cfd6`

## Retrieval Guidance

- Use When: 需要按示例改写自己的 pg_hba.conf 规则。
- Retrieval Keywords: pg_hba examples, trust localhost, scram-sha-256, md5 exception, reject, hostgssenc, regular expression, @admins, +support
- Follow-up Guidance: 示例需结合实际网络、角色和安全要求调整。
- Classification Note: 提供 trust、ident、scram、md5、reject、hostgssenc、regex、@ 文件、+role 等 HBA 示例。

## Official Source Content

## Example `pg_hba.conf` Entries

```
