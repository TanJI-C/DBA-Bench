# Certificate Authentication

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/06_client_authentication.md`
- Source Title: `Client Authentication`
- Source Heading Path: `Client Authentication > Certificate Authentication`
- Source Line Ranges: `1497-1521`
- Chunk ID: `pg16_configuration_0101_f5c5560459`
- Review Status: `needs_human_review`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9b424eb92a993b4141f62545379a2187586358673ed1fca4789297996b4c1e92`

## Retrieval Guidance

- Use When: 需要使用客户端证书作为登录身份凭据。
- Retrieval Keywords: certificate authentication, cert, SSL client certificate, Common Name, clientcert=verify-full, map
- Follow-up Guidance: 必须配置 SSL 和受信 CA；cert auth 与 clientcert 组合时避免冗余/误解。
- Classification Note: 定义 cert 方法、SSL 客户端证书、CN/用户名匹配和 map 选项。

## Official Source Content

## Certificate Authentication

This authentication method uses SSL client certificates to perform
authentication. It is therefore only available for SSL connections;
see [ssl-openssl-config](#ssl-openssl-config) for SSL configuration instructions.
When using this authentication method, the server will require that
the client provide a valid, trusted certificate.  No password prompt
will be sent to the client.  The `cn` (Common Name)
attribute of the certificate
will be compared to the requested database user name, and if they match
the login will be allowed.  User name mapping can be used to allow
`cn` to be different from the database user name.

The following configuration options are supported for SSL certificate
authentication:

**`map`**
: Allows for mapping between system and database user names. See
[auth-username-maps](#auth-username-maps) for details.

It is redundant to use the `clientcert` option with
`cert` authentication because `cert`
authentication is effectively `trust` authentication
with `clientcert=verify-full`.
