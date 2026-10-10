# Getting the Source

## Knowledge Metadata

- Knowledge Type: `solution`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/02_installation_from_source_code.md`
- Source Title: `Installation from Source Code`
- Source Heading Path: `Installation from Source Code > Getting the Source`
- Source Line Ranges: `202-223`
- Chunk ID: `pg16_solution_0002_96c7a7273a`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ad4fd10d8d40e09c16c16b4161f906aafa441a72068c035d9981a684eeb40a8c`

## Retrieval Guidance

- Use When: 需要获取 PostgreSQL 源码开始编译。
- Retrieval Keywords: source tarball, postgresql-version.tar.gz, tar xf, Git checkout
- Follow-up Guidance: 确认要构建的是 release tarball 还是 Git checkout。
- Classification Note: 说明下载源码包、解包和 Git 获取源码的方法。

## Official Source Content

## Getting the Source

The PostgreSQL source code for released versions
can be obtained from the download section of our website:
[](https://www.postgresql.org/ftp/source/).
Download the
`postgresql-`version`.tar.gz`
or `postgresql-`version`.tar.bz2`
file you're interested in, then unpack it:

```
tar xf postgresql-`version`.tar.bz2
```

This will create a directory
`postgresql-`version`` under
the current directory with the PostgreSQL sources.
Change into that directory for the rest of the installation procedure.

Alternatively, you can use the Git version control system; see
[git](#git) for more information.
