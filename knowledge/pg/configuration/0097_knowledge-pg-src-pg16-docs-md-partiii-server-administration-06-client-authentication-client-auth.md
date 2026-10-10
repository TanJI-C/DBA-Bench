# Ident Authentication

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/06_client_authentication.md`
- Source Title: `Client Authentication`
- Source Heading Path: `Client Authentication > Ident Authentication`
- Source Line Ranges: `1138-1193`
- Chunk ID: `pg16_configuration_0097_8a550941ea`
- Review Status: `needs_human_review`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `620715dd509755eb1a35439762f1d6a7685d5c8c197d654b93c45ce927e0f56c`

## Retrieval Guidance

- Use When: 受控闭合网络中需要基于客户端 OS 用户认证 TCP/IP 连接。
- Retrieval Keywords: ident authentication, RFC 1413, port 113, map, client machine trusted
- Follow-up Guidance: 不可信客户端可伪造 ident 返回值，通常不适合开放网络。
- Classification Note: 定义通过客户端 ident server 获取 OS 用户名以及 map 选项和信任边界。

## Official Source Content

## Ident Authentication

The ident authentication method works by obtaining the client's
operating system user name from an ident server and using it as
the allowed database user name (with an optional user name mapping).
This is only supported on TCP/IP connections.

> **Note:**

> When ident is specified for a local (non-TCP/IP) connection,
> peer authentication (see [auth-peer](#auth-peer)) will be
> used instead.
>

The following configuration options are supported for `ident`:

**`map`**
: Allows for mapping between system and database user names. See
[auth-username-maps](#auth-username-maps) for details.

The "Identification Protocol" is described in
[RFC 1413](https://datatracker.ietf.org/doc/html/rfc1413).
Virtually every Unix-like
operating system ships with an ident server that listens on TCP
port 113 by default. The basic functionality of an ident server
is to answer questions like "What user initiated the
connection that goes out of your port `X`
and connects to my port `Y`?".
Since PostgreSQL knows both `X` and
`Y` when a physical connection is established, it
can interrogate the ident server on the host of the connecting
client and can theoretically determine the operating system user
for any given connection.

The drawback of this procedure is that it depends on the integrity
of the client: if the client machine is untrusted or compromised,
an attacker could run just about any program on port 113 and
return any user name they choose. This authentication method is
therefore only appropriate for closed networks where each client
machine is under tight control and where the database and system
administrators operate in close contact. In other words, you must
trust the machine running the ident server.
Heed the warning:

RFC 1413

The Identification Protocol is not intended as an authorization
or access control protocol.

Some ident servers have a nonstandard option that causes the returned
user name to be encrypted, using a key that only the originating
machine's administrator knows.  This option *must not* be
used when using the ident server with PostgreSQL,
since PostgreSQL does not have any way to decrypt the
returned string to determine the actual user name.
