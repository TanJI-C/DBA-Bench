# BSD Authentication

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/06_client_authentication.md`
- Source Title: `Client Authentication`
- Source Heading Path: `Client Authentication > BSD Authentication`
- Source Line Ranges: `1557-1580`
- Chunk ID: `pg16_configuration_0103_eefbad9fcd`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d366360feea11fbe9a56b624297a6d3132b6901e2babe24809d449ca41c94b20`

## Retrieval Guidance

- Use When: OpenBSD 上需要使用 BSD Authentication。
- Retrieval Keywords: BSD Authentication, OpenBSD, auth-postgresql, login.conf, auth group
- Follow-up Guidance: 确保运行 PostgreSQL 的 OS 用户加入 auth 组。
- Classification Note: 定义 OpenBSD BSD Authentication、auth-postgresql login type 和 auth group 要求。

## Official Source Content

## BSD Authentication

This authentication method operates similarly to
`password` except that it uses BSD Authentication
to verify the password. BSD Authentication is used only
to validate user name/password pairs. Therefore the user's role must
already exist in the database before BSD Authentication can be used
for authentication. The BSD Authentication framework is currently
only available on OpenBSD.

BSD Authentication in PostgreSQL uses
the `auth-postgresql` login type and authenticates with
the `postgresql` login class if that's defined
in `login.conf`. By default that login class does not
exist, and PostgreSQL will use the default login class.

> **Note:**

> To use BSD Authentication, the PostgreSQL user account (that is, the
> operating system user running the server) must first be added to
> the `auth` group.  The `auth` group
> exists by default on OpenBSD systems.
>
