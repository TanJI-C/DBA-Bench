# Short Options

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/05_server_configuration.md`
- Source Title: `Server Configuration`
- Source Heading Path: `Server Configuration > Short Options`
- Source Line Ranges: `6716-6743`
- Chunk ID: `pg16_fact_0013_8c5b57d316`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7567e26ec31fdbe658345cf7f0e6329c79c198c1af79c289fddf702f53853791`

## Retrieval Guidance

- Use When: 需要解释 postgres 命令行短选项等价于哪些配置参数。
- Retrieval Keywords: short options, -B, -d, -F, -h, -i, -k, -l, shared_buffers, fsync, listen_addresses
- Follow-up Guidance: 短选项多为历史原因，不代表推荐频繁使用。
- Classification Note: 列出 postgres 单字母命令行选项到 GUC 的映射，属于参考表。

## Official Source Content

## Short Options

For convenience there are also single letter command-line option
switches available for some parameters.  They are described in
[runtime-config-short-table](#runtime-config-short-table).  Some of these
options exist for historical reasons, and their presence as a
single-letter option does not necessarily indicate an endorsement
to use the option heavily.

| Short Option | Equivalent |
| --- | --- |
| `-B `x`` | `shared_buffers = `x`` |
| `-d `x`` | `log_min_messages = DEBUG`x`` |
| `-e` | `datestyle = euro` |
| `-fb`, `-fh`, `-fi`,           `-fm`, `-fn`, `-fo`,           `-fs`, `-ft` | `enable_bitmapscan = off`,           `enable_hashjoin = off`,           `enable_indexscan = off`,           `enable_mergejoin = off`,           `enable_nestloop = off`,           `enable_indexonlyscan = off`,           `enable_seqscan = off`,           `enable_tidscan = off` |
| `-F` | `fsync = off` |
| `-h `x`` | `listen_addresses = `x`` |
| `-i` | `listen_addresses = '*'` |
| `-k `x`` | `unix_socket_directories = `x`` |
| `-l` | `ssl = on` |
| `-N `x`` | `max_connections = `x`` |
| `-O` | `allow_system_table_mods = on` |
| `-p `x`` | `port = `x`` |
| `-P` | `ignore_system_indexes = on` |
| `-s` | `log_statement_stats = on` |
| `-S `x`` | `work_mem = `x`` |
| `-tpa`, `-tpl`, `-te` | `log_parser_stats = on`,         `log_planner_stats = on`,         `log_executor_stats = on` |
| `-W `x`` | `post_auth_delay = `x`` |
