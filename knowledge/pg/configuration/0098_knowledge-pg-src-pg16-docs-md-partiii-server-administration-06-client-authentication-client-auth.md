# Peer Authentication

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/06_client_authentication.md`
- Source Title: `Client Authentication`
- Source Heading Path: `Client Authentication > Peer Authentication`
- Source Line Ranges: `1194-1214`
- Chunk ID: `pg16_configuration_0098_d4026d3fcf`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4ae50217ee583f18518a40d4ba612cebe6735a807bc6282b5f76152393c042bb`

## Retrieval Guidance

- Use When: 本地 Unix socket 连接需要用 OS 用户身份认证。
- Retrieval Keywords: peer authentication, local connections, getpeereid, SO_PEERCRED, map, Unix socket
- Follow-up Guidance: 仅支持具备 peer credential 机制的 OS。
- Classification Note: 定义本地连接通过内核获取客户端 OS 用户并可用 map 映射。

## Official Source Content

## Peer Authentication

The peer authentication method works by obtaining the client's
operating system user name from the kernel and using it as the
allowed database user name (with optional user name mapping). This
method is only supported on local connections.

The following configuration options are supported for `peer`:

**`map`**
: Allows for mapping between system and database user names. See
[auth-username-maps](#auth-username-maps) for details.

Peer authentication is only available on operating systems providing
the `getpeereid()` function, the `SO_PEERCRED`
socket parameter, or similar mechanisms.  Currently that includes
Linux,
most flavors of BSD including
macOS,
and Solaris.
