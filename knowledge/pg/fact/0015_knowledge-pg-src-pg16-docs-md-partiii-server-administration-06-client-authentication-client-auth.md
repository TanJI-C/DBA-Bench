# Authentication Methods

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/06_client_authentication.md`
- Source Title: `Client Authentication`
- Source Heading Path: `Client Authentication > Authentication Methods`
- Source Line Ranges: `776-822`
- Chunk ID: `pg16_fact_0015_e2ff8325a8`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `16b7f8ef7f8b43212c4d79b1e5cffed0f75179ea2e7ca0fd39e4be64bfbfcd02`

## Retrieval Guidance

- Use When: 需要选择认证方法的大方向。
- Retrieval Keywords: Trust authentication, Password authentication, GSSAPI, SSPI, Ident, Peer, LDAP, RADIUS, Certificate, PAM, BSD
- Follow-up Guidance: 远程连接通常密码最简单，本地通常 peer，其他方法需要外部基础设施。
- Classification Note: 总览 trust/password/GSSAPI/SSPI/ident/peer/LDAP/RADIUS/cert/PAM/BSD 的适用场景。

## Official Source Content

## Authentication Methods

PostgreSQL provides various methods for
authenticating users:

- [Trust authentication](#auth-trust), which
simply trusts that users are who they say they are.
- [Password authentication](#auth-password), which
requires that users send a password.
- [GSSAPI authentication](#gssapi-auth), which
relies on a GSSAPI-compatible security library.  Typically this is
used to access an authentication server such as a Kerberos or
Microsoft Active Directory server.
- [SSPI authentication](#sspi-auth), which
uses a Windows-specific protocol similar to GSSAPI.
- [Ident authentication](#auth-ident), which
relies on an "Identification Protocol"
([RFC 1413](https://datatracker.ietf.org/doc/html/rfc1413))
service on the client's machine.  (On local Unix-socket connections,
this is treated as peer authentication.)
- [Peer authentication](#auth-peer), which
relies on operating system facilities to identify the process at the
other end of a local connection.  This is not supported for remote
connections.
- [LDAP authentication](#auth-ldap), which
relies on an LDAP authentication server.
- [RADIUS authentication](#auth-radius), which
relies on a RADIUS authentication server.
- [Certificate authentication](#auth-cert), which
requires an SSL connection and authenticates users by checking the
SSL certificate they send.
- [PAM authentication](#auth-pam), which
relies on a PAM (Pluggable Authentication Modules) library.
- [BSD authentication](#auth-bsd), which
relies on the BSD Authentication framework (currently available
only on OpenBSD).

Peer authentication is usually recommendable for local connections,
though trust authentication might be sufficient in some circumstances.
Password authentication is the easiest choice for remote connections.
All the other options require some kind of external security
infrastructure (usually an authentication server or a certificate
authority for issuing SSL certificates), or are platform-specific.

The following sections describe each of these authentication methods
in more detail.
